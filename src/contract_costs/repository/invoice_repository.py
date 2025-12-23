from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.invoice import Invoice, InvoiceStatus


class InvoiceRepository(ABC):

    @abstractmethod
    def add(self, invoice: Invoice) -> None:
        """Persist new invoice"""
        ...

    @abstractmethod
    def get(self, invoice_id: UUID) -> Invoice | None:
        ...

    @abstractmethod
    def list_invoices(self) -> list[Invoice]:
        ...

    @abstractmethod
    def update(self, invoice: Invoice) -> None:
        ...

    @abstractmethod
    def exists(self, invoice_id: UUID) -> bool:
        ...

    @abstractmethod
    def get_by_invoice_number(self, invoice_number: str) -> Invoice | None:
        ...

    @abstractmethod
    def get_unique_invoice(self, invoice_number: str,seller_id: UUID) -> Invoice | None:
        ...

    @abstractmethod
    def get_for_assignment(self, status: InvoiceStatus | list[InvoiceStatus]) -> list[Invoice]:
        """
        Return invoices that require assignment
        (status NEW or IN_PROGRESS)
        """
        ...
