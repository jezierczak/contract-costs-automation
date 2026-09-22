import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.financial_record import FinancialRecord, FinancialRecordStatus
from contract_costs.model.financial_record_payment import FinancialRecordPayment
from contract_costs.services.financial_records.actions.dto.invoice_action_command import FinancialRecordActionCommand, FinancialRecordAction
from contract_costs.services.financial_records.actions.financial_record_selector_resolver import FinancialRecordSelectorResolver
from contract_costs.unit_of_work import UnitOfWork


logger = logging.getLogger(__name__)

class FinancialRecordActionService(
    ActionHandler[FinancialRecordActionCommand, None]
):
    def __init__(   self,
                    clock: Callable[[], datetime] = utc_now,
                 ):
        self._clock = clock

    def execute(
            self,
            *,
            action: FinancialRecordActionCommand,
            uow:UnitOfWork,
    ) -> None:
        record_repo = uow.financial_records
        selector_resolver = FinancialRecordSelectorResolver(record_repo)

        record_ids = selector_resolver.resolve(
            organization_id=action.organization_id,
            selectors=action.selectors)

        match action.action:
            case FinancialRecordAction.MARK_PAID:
                self._mark_paid(
                    uow=uow,
                    record_ids=record_ids,
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                    payload=action.payload,
                )

            case FinancialRecordAction.MARK_SENT_TO_ACCOUNTANT:
                self._mark_sent_to_accountant(
                    uow=uow,
                    record_ids=record_ids,
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                )

            case FinancialRecordAction.MARK_UNPAID:
                self._mark_unpaid(
                    uow=uow,
                    record_ids=record_ids,
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                )

            case FinancialRecordAction.ADD_PAYMENT:
                self._add_payment(
                    uow=uow,
                    record_ids=record_ids,
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                    payload=action.payload,
                )

            case FinancialRecordAction.REMOVE_PAYMENT:
                self._remove_payment(
                    uow=uow,
                    record_ids=record_ids,
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                    payload=action.payload,
                )

            case FinancialRecordAction.REOPEN:
                self._reopen(
                    uow=uow,
                    record_ids=record_ids,
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                )

            case FinancialRecordAction.DELETE:
                self._delete(
                    uow=uow,
                    record_ids=record_ids,
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                )
            case FinancialRecordAction.TO_IN_PROGRESS:
                self._to_in_progress(
                    uow=uow,
                    record_ids=record_ids,
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                )

            case _:
                raise NotImplementedError(f"Action {action.action} not implemented")

    def _mark_paid(
        self,
        *,
        uow:UnitOfWork,
        organization_id: UUID,
        actor_user_id: UUID,
        record_ids: list[UUID],
        payload: dict[str, Any] | None,
    ) -> None:

        paid_date: date = (payload or {}).get("paid_date") or self._clock().date()

        for record_id in record_ids:
            record = self._require_record(uow=uow,organization_id=organization_id,record_id=record_id)

            total = self._total_cashflow(uow=uow, organization_id=organization_id, record_id=record_id)
            already_paid = self._sum_payments(
                uow=uow, organization_id=organization_id, record_id=record_id,
            )
            remaining = total - already_paid

            if total <= 0:
                # brak przepływu pieniężnego (np. same linie non_cash_cost) – nie ma czego płacić
                self._recompute_payment_state(
                    uow=uow,
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    record=record,
                )
                continue

            if remaining <= 0:
                continue  # już w pełni zapłacone / nadpłacone – no-op

            payment = FinancialRecordPayment(
                id=new_uuid(),
                organization_id=organization_id,
                created_at=self._clock(),
                created_by_user_id=actor_user_id,
                updated_at=None,
                updated_by_user_id=None,
                financial_record_id=record_id,
                amount=remaining,
                paid_date=paid_date,
            )
            uow.financial_record_payments.add(organization_id=organization_id, payment=payment)

            self._recompute_payment_state(
                uow=uow,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                record=record,
            )

    def _add_payment(
        self,
        *,
        uow: UnitOfWork,
        organization_id: UUID,
        actor_user_id: UUID,
        record_ids: list[UUID],
        payload: dict[str, Any] | None,
    ) -> None:

        if not payload or payload.get("amount") is None or payload.get("paid_date") is None:
            raise ValueError("ADD_PAYMENT requires 'amount' and 'paid_date' in payload")

        amount: Decimal = payload["amount"]
        paid_date: date = payload["paid_date"]

        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        for record_id in record_ids:
            record = self._require_record(uow=uow, organization_id=organization_id, record_id=record_id)

            payment = FinancialRecordPayment(
                id=new_uuid(),
                organization_id=organization_id,
                created_at=self._clock(),
                created_by_user_id=actor_user_id,
                updated_at=None,
                updated_by_user_id=None,
                financial_record_id=record_id,
                amount=amount,
                paid_date=paid_date,
            )
            uow.financial_record_payments.add(organization_id=organization_id, payment=payment)

            self._recompute_payment_state(
                uow=uow,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                record=record,
            )

    def _remove_payment(
        self,
        *,
        uow: UnitOfWork,
        organization_id: UUID,
        actor_user_id: UUID,
        record_ids: list[UUID],
        payload: dict[str, Any] | None,
    ) -> None:

        if not payload or payload.get("payment_id") is None:
            raise ValueError("REMOVE_PAYMENT requires 'payment_id' in payload")

        payment_id: UUID = payload["payment_id"]

        for record_id in record_ids:
            record = self._require_record(uow=uow, organization_id=organization_id, record_id=record_id)

            payment = uow.financial_record_payments.get(
                organization_id=organization_id, payment_id=payment_id,
            )
            if not payment or payment.financial_record_id != record_id:
                raise ValueError(
                    f"Payment {payment_id} not found for record {record_id}"
                )

            uow.financial_record_payments.delete(
                organization_id=organization_id, payment_id=payment_id,
            )

            self._recompute_payment_state(
                uow=uow,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                record=record,
            )

    def _mark_sent_to_accountant(self,
                                 *,
                                 uow:UnitOfWork,
                                 organization_id: UUID,
                                 actor_user_id: UUID,
                                 record_ids: list[UUID]) -> None:
        for record_id in record_ids:
            record = self._require_record(uow=uow,organization_id=organization_id,record_id=record_id)

            if record.status != FinancialRecordStatus.PROCESSED:
                logger.warning( f"Invoice {record.reference} "
                    f"cannot be sent to accountant from status {record.status}, SKIPPED")
                continue
                # raise ValueError(
                #     f"Invoice {invoice.invoice_number} "
                #     f"cannot be sent to accountant from status {invoice.status}"
                # )

            updated = record.mark_sent_to_accountant(
                updated_at=self._clock(),
                updated_by_user_id=actor_user_id,
            )
            uow.financial_records.update(updated)

    def _mark_unpaid(self,
                     *,
                     uow:UnitOfWork,
                     organization_id: UUID,
                     actor_user_id: UUID,
                     record_ids: list[UUID]) -> None:
        """
        Świadomy reset: kasuje CAŁĄ historię wpłat faktury.
        """
        for record_id in record_ids:
            record = self._require_record(uow=uow,organization_id=organization_id,record_id=record_id)

            uow.financial_record_payments.delete_all_by_financial_record(
                organization_id=organization_id, financial_record_id=record_id,
            )

            self._recompute_payment_state(
                uow=uow,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                record=record,
            )

    def _delete(
            self,
            *,
            uow: UnitOfWork,
            organization_id: UUID,
            actor_user_id: UUID,
            record_ids: list[UUID],
    ) -> None:

        for record_id in record_ids:
            record = self._require_record(
                uow=uow,
                organization_id=organization_id,
                record_id=record_id,
            )

            # ===== VALIDATION =====
            if record.status in (
                    FinancialRecordStatus.PROCESSED,
                    FinancialRecordStatus.SENT_TO_ACCOUNTANT,
            ):
                raise ValueError(
                    f"Invoice {record.reference} cannot be deleted from status {record.status}"
                )

            # już usunięty -> skip (idempotent)
            if record.status == FinancialRecordStatus.DELETED:
                continue

            # ===== DOMAIN ACTION =====
            updated = record.delete(
                updated_at=self._clock(),
                updated_by_user_id=actor_user_id,
            )

            uow.financial_records.update(updated)

    def _to_in_progress(
            self,
            *,
            uow: UnitOfWork,
            organization_id: UUID,
            actor_user_id: UUID,
            record_ids: list[UUID],
    ) -> None:

        for record_id in record_ids:
            record = self._require_record(
                uow=uow,
                organization_id=organization_id,
                record_id=record_id,
            )

            # walidacja — tylko DELETED można przywrócić
            if record.status != FinancialRecordStatus.DELETED:
                raise ValueError(
                    f"Invoice {record.reference} is not deleted"
                )

            updated = record.to_in_progress(
                updated_at=self._clock(),
                updated_by_user_id=actor_user_id,
            )

            uow.financial_records.update(updated)

    def _reopen(self,
                *,
                uow: UnitOfWork,
                organization_id: UUID,
                actor_user_id: UUID,
                record_ids: list[UUID]) -> None:

        for record_id in record_ids:
            record = self._require_record(uow=uow,organization_id=organization_id,record_id=record_id)

            if record.status not in (
                    FinancialRecordStatus.SENT_TO_ACCOUNTANT,
                    FinancialRecordStatus.PROCESSED,
            ):
                raise ValueError(
                    f"Invoice {record.reference} is not closed or processed"
                )

            updated = record.reopen(
                updated_at=self._clock(),
                updated_by_user_id=actor_user_id
            )
            uow.financial_records.update(updated)
    @staticmethod
    def _total_cashflow(
            *,
            uow: UnitOfWork,
            organization_id: UUID,
            record_id: UUID,
    ) -> Decimal:
        lines = uow.financial_record_lines.list_by_financial_record(
            organization_id=organization_id, financial_record_id=record_id,
        )
        return sum((line.amount.cashflow for line in lines), Decimal("0"))

    @staticmethod
    def _sum_payments(
            *,
            uow: UnitOfWork,
            organization_id: UUID,
            record_id: UUID,
    ) -> Decimal:
        payments = uow.financial_record_payments.list_by_financial_record(
            organization_id=organization_id, financial_record_id=record_id,
        )
        return sum((p.amount for p in payments), Decimal("0"))

    def _recompute_payment_state(
            self,
            *,
            uow: UnitOfWork,
            organization_id: UUID,
            actor_user_id: UUID,
            record: FinancialRecord,
    ) -> None:
        """
        payment_status i paid_date faktury są zawsze pochodną listy wpłat
        vs. sumy cashflow jej pozycji – przeliczane po każdej zmianie wpłat.
        """
        total = self._total_cashflow(
            uow=uow, organization_id=organization_id, record_id=record.id,
        )
        payments = uow.financial_record_payments.list_by_financial_record(
            organization_id=organization_id, financial_record_id=record.id,
        )
        paid = sum((p.amount for p in payments), Decimal("0"))
        last_paid_date = max((p.paid_date for p in payments), default=None)

        now = self._clock()

        if total <= 0:
            # brak przepływu pieniężnego (np. same linie non_cash_cost) – z automatu "zapłacone"
            updated = record.mark_paid(
                paid_at=last_paid_date, updated_at=now, updated_by_user_id=actor_user_id,
            )
        elif paid <= 0:
            updated = record.mark_unpaid(
                updated_at=now, updated_by_user_id=actor_user_id,
            )
        elif paid < total:
            updated = record.mark_partially_paid(
                paid_at=last_paid_date, updated_at=now, updated_by_user_id=actor_user_id,
            )
        else:
            updated = record.mark_paid(
                paid_at=last_paid_date, updated_at=now, updated_by_user_id=actor_user_id,
            )

        uow.financial_records.update(updated)

    @staticmethod
    def _require_record(
            uow: UnitOfWork,
            organization_id: UUID,
            record_id: UUID,
    ) -> FinancialRecord:

        record = uow.financial_records.get(organization_id=organization_id,record_id=record_id)
        if not record:
            raise ValueError(f"Financial record {record_id} not found")

        return record