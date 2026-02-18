import logging
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.model.financial_record import PaymentStatus, FinancialRecord, FinancialRecordStatus
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

            case FinancialRecordAction.REOPEN:
                self._reopen(
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

        paid_at = None
        if payload:
            paid_at = payload.get("paid_at")

        for record_id in record_ids:
            record = self._require_record(uow=uow,organization_id=organization_id,record_id=record_id)

            if record.payment_status == PaymentStatus.PAID:
                continue  # albo raise, zależnie od filozofii

            updated = record.mark_paid(
                paid_at=paid_at,
                updated_at=self._clock(),
                updated_by_user_id=actor_user_id,
            )
            uow.financial_records.update(updated)

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
        for record_id in record_ids:
            record = self._require_record(uow=uow,organization_id=organization_id,record_id=record_id)

            if record.payment_status == PaymentStatus.UNPAID:
                continue

            updated = record.mark_unpaid(
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
    def _require_record(
            uow: UnitOfWork,
            organization_id: UUID,
            record_id: UUID,
    ) -> FinancialRecord:

        record = uow.financial_records.get(organization_id=organization_id,record_id=record_id)
        if not record:
            raise ValueError(f"Financial record {record_id} not found")

        return record