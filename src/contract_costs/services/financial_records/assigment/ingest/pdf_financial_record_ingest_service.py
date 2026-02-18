import logging
from dataclasses import replace
from uuid import UUID

from contract_costs.model.financial_record import FinancialRecord, FinancialRecordStatus
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_ref_result import (
    FinancialRecordRefResult,
    RecordApplyAction,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import ResolvedFinancialRecordUpdate
from contract_costs.services.financial_records.assigment.ingest.financial_record_ingest_service import FinancialRecordIngestService
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class PdfFinancialRecordIngestService(FinancialRecordIngestService):
    """
    PDF ingest:
    - nie ufa numerom faktur
    - wykrywa kolizje OCR
    - nigdy nie DELETE
    - nigdy nie PROCESSED
    """


    def apply(
        self,
        *,
        uow: UnitOfWork,
        organization_id: UUID,
        actor_user_id: UUID,
        updates: list[ResolvedFinancialRecordUpdate],
    ) -> dict[str, FinancialRecordRefResult]:
        record_repo=uow.financial_records
        results: dict[str, FinancialRecordRefResult] = {}

        for update in updates:
            if not update.reference or not update.reference.strip():
                raise ValueError("PDF ingest requires invoice reference (even placeholder)")

            existing = self._get_existing_record(
                organization_id=organization_id,
                update=update,
                record_repo=record_repo

            )

            # -------------------------------------------------
            # OCR COLLISION → suffix -duplicate
            # -------------------------------------------------
            if existing is not None:
                logger.warning(
                    "OCR collision detected for record %s → creating duplicate",
                    update.reference,
                )
                update = replace(
                    update,
                    reference=f"{update.reference}-duplicate",
                )

            ref_key = update.reference

            if ref_key in results:
                raise ValueError(f"Duplicate record reference in batch: {ref_key}")

            # -------------------------------------------------
            # CREATE ONLY (PDF never modifies existing records)
            # -------------------------------------------------
            now = self._clock()
            record_id = self._id_generator()

            record = FinancialRecord(
                id=record_id,
                organization_id=organization_id,
                reference=update.reference,
                invoice_date=update.invoice_date,
                selling_date=update.selling_date,
                buyer_id=update.buyer.id,
                seller_id=update.seller.id,
                payment_method=update.payment_method,
                due_date=update.due_date,
                paid_date=update.paid_date,
                payment_status=update.payment_status,
                status=update.status or FinancialRecordStatus.NEW_COST,
                timestamp=now,
                tags=self._resolve_tags(update.tags),
                # scan_filename=update.,
                created_at=now,
                created_by_user_id=actor_user_id,
                updated_at=None,
                updated_by_user_id=None,
                documents=[],
            )

            record_repo.add(record)

            results[ref_key] = FinancialRecordRefResult(
                record_id=record_id,
                action=RecordApplyAction.APPLIED,
                record_reference=record.reference,
                old_record_reference=update.old_record_reference,
                buyer_role=update.buyer.role,
                seller_role=update.seller.role,
            )

        return results
