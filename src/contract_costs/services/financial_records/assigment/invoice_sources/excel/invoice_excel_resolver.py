import logging
from uuid import UUID

from contract_costs.model.company import CompanyType
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator, EvaluateMode
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    InvoiceExcelBatch, ResolvedFinancialRecordUpdate, RecordIngestBatch,
)

logger = logging.getLogger(__name__)


class FinancialRecordExcelBatchResolver:
    def __init__(self, company_evaluate_orchestrator: CompanyEvaluateOrchestrator) -> None:
        self._company_evaluate_orchestrator = company_evaluate_orchestrator

    def resolve(self,
                *,
                organization_id: UUID,
                actor_user_id: UUID,
                batch: InvoiceExcelBatch) -> RecordIngestBatch:
        resolved_invoices: list[ResolvedFinancialRecordUpdate] = []

        for inv in batch.financial_records:
            raw_buyer_nip = inv.buyer_tax_number
            raw_seller_nip = inv.seller_tax_number
            buyer_company = self._company_evaluate_orchestrator.evaluate_from_tax(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                input_tax_number=raw_buyer_nip,
                role=CompanyType.BUYER)#, mode=EvaluateMode.NO_CREATE)
            seller_company = self._company_evaluate_orchestrator.evaluate_from_tax(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                input_tax_number=
                raw_seller_nip,
                role=CompanyType.SELLER)
            # if buyer_company.role != CompanyType.OWN:
            #     logger.error(f"Buyer: {buyer_company.name} evaluated by NIP: {raw_buyer_nip} is not OWN company, and cannot act as buyer in cost invoice")
            #     raise RuntimeError(f"Buyer company role must be OWN! Wrong NIP: {raw_buyer_nip}")

            resolved_invoices.append(
                ResolvedFinancialRecordUpdate(
                    command=inv.command,

                    reference=inv.reference,
                    record_id=inv.record_id,
                    old_record_reference=inv.old_reference,

                    invoice_date=inv.invoice_date,
                    selling_date=inv.selling_date,

                    buyer=buyer_company,
                    seller=seller_company,

                    payment_method=inv.payment_method,
                    due_date=inv.due_date,
                    payment_status=inv.payment_status,
                    status=inv.status,
                    # scan_filename=inv.scan_filename,
                    paid_date = inv.paid_date,
                    tags=inv.tags,
                )
            )

        return RecordIngestBatch(
            financial_records=resolved_invoices,
            lines=batch.lines,
        )
