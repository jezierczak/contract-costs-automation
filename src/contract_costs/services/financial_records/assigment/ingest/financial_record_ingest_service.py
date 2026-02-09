from abc import ABC, abstractmethod
from dataclasses import replace
from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.company import Company, CompanyType
from contract_costs.model.financial_record import FinancialRecord, FinancialRecordStatus
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_ref_result import FinancialRecordRefResult
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import ResolvedFinancialRecordUpdate


class FinancialRecordIngestService(ABC):
    def __init__(self,
                 record_repository: FinancialRecordRepository,
                 id_generator: Callable[[], UUID] = new_uuid,
                 clock: Callable[[], datetime] = utc_now,
                 ) -> None:
        self._record_repository = record_repository
        self._id_generator = id_generator
        self._clock = clock


    @abstractmethod
    def apply(
            self,
            *,
            organization_id: UUID,
            actor_user_id: UUID,
            updates: list[ResolvedFinancialRecordUpdate],
    ) -> dict[str, FinancialRecordRefResult]:
        ...

    def _get_existing_record(
        self,
            *,
            organization_id: UUID,
        update: ResolvedFinancialRecordUpdate,
    ) -> FinancialRecord | None:
        if update.record_id:
            return self._record_repository.get(
                organization_id=organization_id,
                record_id=update.record_id)

        ref = update.reference
        if not ref: return None
        return self._record_repository.get_unique_record(
            organization_id=organization_id,
            reference=ref,
            seller_id=update.seller.id,
        )

    def mark_processed(
            self,
            *,
            organization_id: UUID,
            actor_user_id: UUID,
            record_ids: list[UUID],
    ) -> None:
        for rec_id in record_ids:
            record = self._record_repository.get(organization_id=organization_id, record_id=rec_id)
            if not record or record.status == FinancialRecordStatus.PROCESSED:
                continue

            now = self._clock()
            updated = replace(
                record,
                status=FinancialRecordStatus.PROCESSED,
                updated_at=now,
                updated_by_user_id=actor_user_id,
            )
            self._record_repository.update(updated)
            self._record_repository.update(updated)

    @staticmethod
    def _resolve_tags(tags: str | None) -> set[str]:
        return {t.strip() for t in tags.split(",") if t.strip()} if tags else set()

