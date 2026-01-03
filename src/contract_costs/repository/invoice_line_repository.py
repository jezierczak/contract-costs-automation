from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.invoice import InvoiceStatus
from contract_costs.model.invoice_line import InvoiceLine


class InvoiceLineRepository(ABC):

    @abstractmethod
    def add(self, invoice_line: InvoiceLine) -> None:
        ...

    @abstractmethod
    def get(self, invoice_line_id: UUID) -> InvoiceLine | None:
        ...

    @abstractmethod
    def list_by_invoice_ids(self, invoice_line_ids: list[UUID]) -> list[InvoiceLine]:
        ...

    @abstractmethod
    def list_by_null_invoice(self) -> list[InvoiceLine]:
        ...

    @abstractmethod
    def list_lines(self) -> list[InvoiceLine]:
        ...

    @abstractmethod
    def list_by_contract(self, contract_id: UUID) -> list[InvoiceLine]:
        ...

    @abstractmethod
    def list_by_invoice(self, invoice_id: UUID) -> list[InvoiceLine]:
        ...

    @abstractmethod
    def update(self, invoice_line: InvoiceLine) -> None:
        ...

    @abstractmethod
    def exists(self, invoice_line_id: UUID) -> bool:
        ...

    @abstractmethod
    def delete_not_in_ids(
            self,
            invoice_id: UUID,
            keep_ids: set[UUID],
    ) -> int:
        ...

    @abstractmethod
    def get_for_assignment(self) -> list[InvoiceLine]:
        """
        Return invoices that require assignment
        (status NEW or IN_PROGRESS)
        """
        ...