import logging

from contract_costs.model.company import CompanyType
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.invoices.dto.common import (
    InvoiceExcelBatch, ResolvedInvoiceUpdate, InvoiceIngestBatch,
)

logger = logging.getLogger(__name__)


class InvoiceExcelBatchResolver:
    def __init__(self, company_evaluate_orchestrator: CompanyEvaluateOrchestrator) -> None:
        self._company_evaluate_orchestrator = company_evaluate_orchestrator

    def resolve(self, batch: InvoiceExcelBatch) -> InvoiceIngestBatch:
        resolved_invoices: list[ResolvedInvoiceUpdate] = []

        for inv in batch.invoices:
            raw_buyer_nip = inv.buyer_tax_number
            raw_seller_nip = inv.seller_tax_number
            buyer_company = self._company_evaluate_orchestrator.evaluate_from_tax(raw_buyer_nip,role=CompanyType.BUYER)
            seller_company = self._company_evaluate_orchestrator.evaluate_from_tax(raw_seller_nip,role=CompanyType.SELLER)
            if buyer_company.role != CompanyType.OWN:
                logger.error(f"Buyer: {buyer_company.name} evaluated by NIP: {raw_buyer_nip} is not OWN company, and cannot act as buyer in cost invoice")
                raise RuntimeError(f"Buyer company role must be OWN! Wrong NIP: {raw_buyer_nip}")

            resolved_invoices.append(
                ResolvedInvoiceUpdate(
                    command=inv.command,

                    invoice_number=inv.invoice_number,
                    old_invoice_number=inv.old_invoice_number,

                    invoice_date=inv.invoice_date,
                    selling_date=inv.selling_date,

                    buyer_id=buyer_company.id,
                    seller_id=seller_company.id,

                    payment_method=inv.payment_method,
                    due_date=inv.due_date,
                    payment_status=inv.payment_status,
                    status=inv.status,
                )
            )

        return InvoiceIngestBatch(
            invoices=resolved_invoices,
            lines=batch.lines,
        )
