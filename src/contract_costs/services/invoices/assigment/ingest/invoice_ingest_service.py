from abc import ABC, abstractmethod
from dataclasses import replace
from uuid import UUID

from contract_costs.model.company import Company, CompanyType
from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.invoices.assigment.ingest.dto.invoice_ref_result import InvoiceRefResult
from contract_costs.services.invoices.assigment.invoice_sources.dto.common import ResolvedInvoiceUpdate


class InvoiceIngestService(ABC):
    def __init__(self, invoice_repository: InvoiceRepository) -> None:
        self._invoice_repository = invoice_repository


    @abstractmethod
    def apply(
        self,
        updates: list[ResolvedInvoiceUpdate],
    ) -> dict[str, InvoiceRefResult]:
        ...

    def _get_existing_invoice(
        self,
        update: ResolvedInvoiceUpdate,
    ) -> Invoice | None:
        if update.invoice_id:
            return self._invoice_repository.get(update.invoice_id)

        ref = update.invoice_number
        if not ref: return None
        return self._invoice_repository.get_unique_invoice(
            ref,
            update.seller.id,
        )

    def mark_processed(self, invoice_ids: list[UUID]) -> None:
        for inv_id in invoice_ids:
            invoice = self._invoice_repository.get(inv_id)
            if not invoice or invoice.status == InvoiceStatus.PROCESSED:
                continue

            updated = replace(invoice, status=InvoiceStatus.PROCESSED)
            self._invoice_repository.update(updated)

    @staticmethod
    def _resolve_tags(tags: str | None) -> set[str]:
        return {t.strip() for t in tags.split(",") if t.strip()} if tags else set()

