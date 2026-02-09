import logging
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

from contract_costs.common.time import utc_now
from contract_costs.model.financial_record import PaymentStatus, FinancialRecord, FinancialRecordStatus
from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.services.financial_records.actions.dto.invoice_action_command import FinancialRecordActionCommand, FinancialRecordAction
from contract_costs.services.financial_records.actions.financial_record_selector_resolver import FinancialRecordSelectorResolver


logger = logging.getLogger(__name__)

class FinancialRecordActionService:
    def __init__(   self,
                    financial_record_repository: FinancialRecordRepository,
                    clock: Callable[[], datetime] = utc_now,
                 ):
        self._record_repo =financial_record_repository
        self._financial_record_selector_resolver = FinancialRecordSelectorResolver(self._record_repo)
        self._clock = clock

    def execute(
            self,
            *,
            organization_id: UUID,
            actor_user_id: UUID,
            cmd: FinancialRecordActionCommand,
    ) -> None:
        record_ids = self._financial_record_selector_resolver.resolve(
            organization_id=organization_id,
            selectors=cmd.selectors)

        match cmd.action:
            case FinancialRecordAction.MARK_PAID:
                self._mark_paid(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    record_ids=record_ids,
                    payload=cmd.payload)

            case FinancialRecordAction.MARK_SENT_TO_ACCOUNTANT:
                self._mark_sent_to_accountant(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    record_ids=record_ids)

            case FinancialRecordAction.MARK_UNPAID:
                self._mark_unpaid(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    record_ids=record_ids)

            case FinancialRecordAction.REOPEN:
                self._reopen(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    record_ids=record_ids)

            case _:
                raise NotImplementedError(f"Action {cmd.action} not implemented")

    def _mark_paid(
        self,
        *,
        organization_id:UUID,
        actor_user_id:UUID,
        record_ids: list[UUID],
        payload: dict[str, Any] | None,
    ) -> None:

        paid_at = None
        if payload:
            paid_at = payload.get("paid_at")

        for record_id in record_ids:
            record = self._require_record(organization_id=organization_id,record_id=record_id)

            if record.payment_status == PaymentStatus.PAID:
                continue  # albo raise, zależnie od filozofii

            updated = record.mark_paid(
                paid_at=paid_at,
                updated_at=self._clock(),
                updated_by_user_id=actor_user_id,
            )
            self._record_repo.update(updated)

    def _mark_sent_to_accountant(self,
                                 *,
                                 organization_id: UUID,
                                 actor_user_id: UUID,
                                 record_ids: list[UUID]) -> None:
        for record_id in record_ids:
            record = self._require_record(organization_id=organization_id,record_id=record_id)

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
            self._record_repo.update(updated)

    def _mark_unpaid(self,
                     *,
                     organization_id: UUID,
                     actor_user_id: UUID,
                     record_ids: list[UUID]) -> None:
        for record_id in record_ids:
            record = self._require_record(organization_id=organization_id,record_id=record_id)

            if record.payment_status == PaymentStatus.UNPAID:
                continue

            updated = record.mark_unpaid(
                updated_at=self._clock(),
                updated_by_user_id=actor_user_id,
            )
            self._record_repo.update(updated)


    def _reopen(self,
                *,
                organization_id: UUID,
                actor_user_id: UUID,
                record_ids: list[UUID]) -> None:

        for record_id in record_ids:
            record = self._require_record(organization_id=organization_id,record_id=record_id)

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
            self._record_repo.update(updated)



    def _require_record(self, organization_id: UUID, record_id: UUID) -> FinancialRecord:
        record = self._record_repo.get(organization_id=organization_id, record_id=record_id)
        if not record:
            raise ValueError(f"Financial record with id {record_id} not found")
        return record