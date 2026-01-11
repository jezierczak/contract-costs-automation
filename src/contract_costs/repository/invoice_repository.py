from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.invoice import Invoice, InvoiceStatus
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery


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
    def get_by_invoice_number(self, invoice_number: str) -> list[Invoice]:
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

    @abstractmethod
    def list_by_seller_id(self, seller_id: UUID) -> list[Invoice]:
        ...

    @abstractmethod
    def list_for_review(self, query: InvoiceReviewQuery) -> list[Invoice]:
        ...