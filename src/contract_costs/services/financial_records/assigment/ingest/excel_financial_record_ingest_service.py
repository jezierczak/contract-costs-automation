import logging
from dataclasses import replace
from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.common.time import utc_now
from contract_costs.model.company import CompanyVerificationStatus
from contract_costs.model.financial_record import FinancialRecord, FinancialRecordStatus
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_validator import \
    RecordCompletionValidator
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_ref_result import (
    FinancialRecordRefResult,
    RecordApplyAction,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import ResolvedFinancialRecordUpdate
from contract_costs.services.financial_records.assigment.ingest.financial_record_ingest_service import FinancialRecordIngestService

import contract_costs.config as cfg
from contract_costs.services.number_generator.number_generator import NumberGenerator
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ExcelFinancialRecordIngestService(FinancialRecordIngestService):
    """
    Excel ingest:
    - source of truth
    - APPLY / MODIFY / DELETE
    - obsługuje old_invoice_number
    - respektuje workflow
    """

    def __init__(
            self,
            file_organizer: DocumentFileOrganizer,
            number_generator: NumberGenerator,
            clock: Callable[[], datetime] = utc_now,
    ):
        super().__init__(clock=clock)
        self._file_organizer = file_organizer
        self._number_generator = number_generator

    def apply(
            self,
            *,
            uow: UnitOfWork,
            organization_id: UUID,
            actor_user_id: UUID,
            updates: list[ResolvedFinancialRecordUpdate],
    ) -> dict[str, FinancialRecordRefResult]:

        record_repo = uow.financial_records
        document_repo = uow.documents

        results: dict[str, FinancialRecordRefResult] = {}

        for update in updates:
            if not update.reference or not update.reference.strip():
                raise ValueError("Excel ingest requires record reference")

            ref_key = update.reference

            if ref_key in results:
                raise ValueError(f"Duplicate invoice reference in batch: {ref_key}")

            existing = self._get_existing_record(
                organization_id=organization_id,
                update=update,
                record_repo=record_repo
            )

            buyer = update.buyer
            seller = update.seller
            # update_direction = self.resolve_direction(buyer,seller)

            # -------------------------------------------------
            # SKIP FINALIZED
            # -------------------------------------------------
            if existing and existing.status in {
                FinancialRecordStatus.PROCESSED,
                FinancialRecordStatus.SENT_TO_ACCOUNTANT,
            }:
                logger.warning(
                    "Skipping finalized invoice %s",
                    existing.reference,
                )
                results[ref_key] = FinancialRecordRefResult(
                    record_id=existing.id,
                    action=RecordApplyAction.SKIPPED,
                    record_reference=existing.reference,
                    old_record_reference=update.old_record_reference,
                    buyer_role=buyer.role,
                    seller_role=seller.role

                )
                continue

            # -------------------------------------------------
            # DELETE (LOGICAL)
            # -------------------------------------------------
            if update.command == InvoiceCommand.DELETE:
                if existing is None:
                    results[ref_key] = FinancialRecordRefResult(
                        record_id=None,
                        action=RecordApplyAction.SKIPPED,
                        record_reference=update.reference,
                        old_record_reference=update.old_record_reference,
                        buyer_role=buyer.role,
                        seller_role=seller.role
                    )
                    continue

                record_repo.update(
                    replace(existing, status=FinancialRecordStatus.DELETED)
                )
                # -------------------------------------------------
                # DETACH DOCUMENTS
                # -------------------------------------------------
                documents = document_repo.list_by_record_id(
                    organization_id=organization_id,
                    record_id=existing.id,
                )

                org_root = cfg.WORK_DIR / str(organization_id)

                for doc in documents:
                    # move file back to RAW
                    raw_relative = self._file_organizer.move_to_raw(
                        root=org_root,
                        file_path=org_root / doc.file_path,
                    )

                    updated_doc = replace(
                        doc,
                        financial_record_id=None,
                        file_path=raw_relative.as_posix(),
                        filename=raw_relative.name,
                    )

                    document_repo.update(updated_doc)

                results[ref_key] = FinancialRecordRefResult(
                    record_id=existing.id,
                    action=RecordApplyAction.DELETED,
                    record_reference=existing.reference,
                    old_record_reference=update.old_record_reference,
                    buyer_role=buyer.role,
                    seller_role=seller.role
                )
                continue

            # -------------------------------------------------
            # BUSINESS RULE:
            # At least one side (buyer or seller) must be OWN
            # for APPLY / CREATE operations
            # -------------------------------------------------
            if not RecordCompletionValidator.resolve_financial_record_direction(buyer.role, seller.role):
                raise RuntimeError(
                    f"Invoice {update.reference} has no OWN company "
                    f"(buyer={buyer.tax_number}, seller={seller.tax_number})"
                )

            # -------------------------------------------------
            # APPLY / MODIFY
            # -------------------------------------------------

            if existing:
                now = self._clock()
                updated = replace(
                    existing,
                    reference=update.reference,
                    invoice_date=update.invoice_date,
                    selling_date=update.selling_date,
                    buyer_id=update.buyer.id,
                    seller_id=update.seller.id,
                    payment_method=update.payment_method,
                    due_date=update.due_date,
                    paid_date=update.paid_date,
                    payment_status=update.payment_status,
                    status=update.status,
                    tags=self._resolve_tags(update.tags),
                    # scan_filename=update.scan_filename,
                    updated_at=now,
                    updated_by_user_id=actor_user_id,
                )
                record_repo.update(updated)

                results[ref_key] = FinancialRecordRefResult(
                    record_id=existing.id,
                    action=RecordApplyAction.APPLIED,
                    record_reference=update.reference,
                    old_record_reference=update.old_record_reference,
                    buyer_role=buyer.role,
                    seller_role=seller.role,
                    companies_verified=(
                        buyer.verification_status == CompanyVerificationStatus.VERIFIED
                        and seller.verification_status == CompanyVerificationStatus.VERIFIED
                    )
                )
                continue

            # -------------------------------------------------
            # CREATE
            # -------------------------------------------------
            generated_reference_number = self._number_generator.generate(
                uow=uow,
                organization_id=organization_id,
                pattern=update.reference,
                date=self._clock())
            old_reference_number = update.reference
            now = self._clock()
            record_id = self._id_generator()

            record = FinancialRecord(
                id=record_id,
                organization_id=organization_id,
                reference=generated_reference_number,#update.reference,
                invoice_date=update.invoice_date,
                selling_date=update.selling_date,
                buyer_id=update.buyer.id,
                seller_id=update.seller.id,
                payment_method=update.payment_method,
                due_date=update.due_date,
                paid_date=update.paid_date,
                payment_status=update.payment_status,
                status=update.status,
                timestamp=now,
                tags=self._resolve_tags(update.tags),
                # scan_filename=update.scan_filename,
                created_at=now,
                created_by_user_id=actor_user_id,
                updated_at=None,
                updated_by_user_id=None,
                documents=[]
            )

            record_repo.add(record)

            results[ref_key] = FinancialRecordRefResult(
                record_id=record_id,
                action=RecordApplyAction.APPLIED,
                record_reference=record.reference,
                old_record_reference=old_reference_number,#update.old_record_reference,
                buyer_role=buyer.role,
                seller_role=seller.role,
                companies_verified=(
                    buyer.verification_status == CompanyVerificationStatus.VERIFIED
                    and seller.verification_status == CompanyVerificationStatus.VERIFIED
                )
            )

        return results
