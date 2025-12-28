import logging

from contract_costs.services.invoices.dto.common import (
    InvoiceExcelBatch, ResolvedInvoiceUpdate, InvoiceIngestBatch,
)
from contract_costs.services.invoices.company_resolve_service import CompanyResolveService

logger = logging.getLogger(__name__)


class InvoiceExcelBatchResolver:
    def __init__(self, company_resolver: CompanyResolveService) -> None:
        self._company_resolver = company_resolver

    def resolve(self, batch: InvoiceExcelBatch) -> InvoiceIngestBatch:
        resolved_invoices: list[ResolvedInvoiceUpdate] = []

        for inv in batch.invoices:
            raw_buyer_nip = inv.buyer_tax_number
            buyer_company = self._company_resolver.find_by_tax_number(raw_buyer_nip)

            if buyer_company is None:
                logger.error(
                    "Invoice import failed: buyer not found",
                    extra={
                        "buyer_tax_number": raw_buyer_nip,
                        "invoice_number": inv.invoice_number,
                        "command": inv.command,
                    },
                )
                raise ValueError(
                    f"Buyer company not found for tax number: {raw_buyer_nip}"
                )

            raw_seller_nip = inv.seller_tax_number

            seller_company = self._company_resolver.find_by_tax_number(raw_seller_nip)

            if seller_company is None:
                seller_company = self._company_resolver.resolve_seller_or_placeholder(
                    raw_seller_nip
                )

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
