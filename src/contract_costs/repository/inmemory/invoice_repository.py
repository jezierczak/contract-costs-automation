from uuid import UUID
from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.repository.invoice_repository import InvoiceRepository


class InMemoryInvoiceRepository(InvoiceRepository):

    def __init__(self) -> None:
        self._invoices: dict[UUID, Invoice] = {}

    def add(self, invoice: Invoice) -> None:
        self._invoices[invoice.id] = invoice

    def get(self, invoice_id: UUID) -> Invoice | None:
        return self._invoices.get(invoice_id)

    def get_by_invoice_number(self, invoice_number: str) -> Invoice | None:
        return [
            inv for inv in self._invoices.values()
            if inv.invoice_number == invoice_number
        ][0]
    def list_invoices(self) -> list[Invoice]:
        return list(self._invoices.values())

    def update(self, invoice: Invoice) -> None:
        self._invoices[invoice.id] = invoice

    def exists(self, invoice_id: UUID) -> bool:
        return invoice_id in self._invoices

    def get_for_assignment(self, status: InvoiceStatus | list[InvoiceStatus]) -> list[Invoice]:
        if isinstance(status, InvoiceStatus):
            return [
                inv for inv in self._invoices.values()
                if inv.status == status
            ]
        return [
            inv for inv in self._invoices.values()
            if inv.status in {status}
        ]

