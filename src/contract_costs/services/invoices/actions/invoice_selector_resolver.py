from uuid import UUID


from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.invoices.actions.dto.invoice_action_command import InvoiceSelector


class InvoiceSelectorResolver:

    def __init__(self, invoice_repo: InvoiceRepository) -> None:
        self._invoice_repo = invoice_repo

    def resolve(self, selectors: list[InvoiceSelector]) -> list[UUID]:
        invoice_ids: list[UUID] = []

        for selector in selectors:
            if selector.invoice_id:
                invoice = self._invoice_repo.get(selector.invoice_id)
                if not invoice:
                    raise ValueError(
                        f"Invoice with id {selector.invoice_id} not found"
                    )
                invoice_ids.append(invoice.id)
                continue

            if selector.invoice_number:
                invoice = self._invoice_repo.get_by_invoice_number(
                    selector.invoice_number
                )
                if not invoice:
                    raise ValueError(
                        f"Invoice with number {selector.invoice_number} not found"
                    )
                invoice_ids.append(invoice.id)
                continue

            # teoretycznie nieosiągalne przez Pydantic
            raise RuntimeError("Invalid invoice selector")

        return invoice_ids
