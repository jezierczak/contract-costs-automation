from dataclasses import replace
from uuid import UUID

from contract_costs.services.invoices.dto.common import (
    InvoiceExcelBatch,
    InvoiceUpdate,
)
from contract_costs.services.invoices.company_resolve_service import CompanyResolveService


class InvoiceExcelBatchResolver:
    def __init__(self, company_resolver: CompanyResolveService) -> None:
        self._company_resolver = company_resolver

    def resolve(self, batch: InvoiceExcelBatch) -> InvoiceExcelBatch:
        resolved_invoices: list[InvoiceUpdate] = []

        for inv in batch.invoices:


            buyer_id = (
                self._company_resolver.find_by_tax_number(inv.buyer_id).id
                if inv.buyer_id is not None
                else None
            )

            seller_id = (
                self._company_resolver.find_by_tax_number(inv.seller_id).id
                if inv.seller_id is not None
                else None
            )

            resolved_invoices.append(
                replace(
                    inv,
                    buyer_id=buyer_id,
                    seller_id=seller_id,
                )
            )

        return InvoiceExcelBatch(
            invoices=resolved_invoices,
            lines=batch.lines,
        )
