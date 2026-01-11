from uuid import UUID
from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery


class InMemoryInvoiceRepository(InvoiceRepository):

    def __init__(self) -> None:
        self._invoices: dict[UUID, Invoice] = {}

    def add(self, invoice: Invoice) -> None:
        self._invoices[invoice.id] = invoice

    def get(self, invoice_id: UUID) -> Invoice | None:
        return self._invoices.get(invoice_id)

    def get_by_invoice_number(self, invoice_number: str) -> list[Invoice]:
        result = []
        for inv in self._invoices.values():
            if inv.invoice_number == invoice_number and inv.status != InvoiceStatus.DELETED:
                result.append(inv)
        return result
    def list_invoices(self) -> list[Invoice]:
        return list(self._invoices.values())

    def update(self, invoice: Invoice) -> None:
        self._invoices[invoice.id] = invoice

    def exists(self, invoice_id: UUID) -> bool:
        return invoice_id in self._invoices

    def get_unique_invoice(self, invoice_number: str, seller_id: UUID) -> Invoice | None:
        for inv in self._invoices.values():
            if (
                    inv.invoice_number == invoice_number
                    and inv.seller_id == seller_id
                    and inv.status != InvoiceStatus.DELETED
            ):
                return inv
        return None

    def get_for_assignment(
            self,
            status: InvoiceStatus | list[InvoiceStatus]
    ) -> list[Invoice]:

        if isinstance(status, InvoiceStatus):
            statuses = {status}
        else:
            statuses = set(status)

        return [
            inv for inv in self._invoices.values()
            if inv.status in statuses
        ]

    def list_by_seller_id(self, seller_id: UUID) -> list[Invoice]:
        return NotImplemented

    def list_for_review(self, query: InvoiceReviewQuery) -> list[Invoice]:
        input_values = self._invoices.values()
        result = list(input_values)
        if query.statuses:
            result = [
                i for i in input_values
                if i.status in query.statuses
            ]

        if query.payment_statuses:
            result = [
                i for i in input_values
                if i.payment_status in query.payment_statuses
            ]

        if query.from_date:
            result = [
                i for i in input_values
                if i.invoice_date and i.invoice_date >= query.from_date
            ]

        if query.to_date:
            result = [
                i for i in input_values
                if i.invoice_date and i.invoice_date <= query.to_date
            ]

        if query.only_ready_for_accountant:
            result = [
                i for i in input_values
                if i.status == InvoiceStatus.PROCESSED
            ]

        return sorted(
            result,
            key=lambda i: (i.invoice_date or i.timestamp),
            reverse=True,
        )
