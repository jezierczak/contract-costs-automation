from uuid import UUID
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository


class InMemoryInvoiceLineRepository(InvoiceLineRepository):

    def __init__(self) -> None:
        self._lines: dict[UUID, InvoiceLine] = {}

    def add(self, invoice_line: InvoiceLine) -> None:
        self._lines[invoice_line.id] = invoice_line

    def get(self, invoice_line_id: UUID) -> InvoiceLine | None:
        return self._lines.get(invoice_line_id)

    def list_by_invoice_ids(self, invoice_line_ids: list[UUID]) -> list[InvoiceLine]:
        return [
            line
            for id_ in invoice_line_ids
            if (line := self.get(id_)) is not None
        ]

    def list_by_null_invoice(self) -> list[InvoiceLine]:
        return [
            line for line in self._lines.values()
            if line.invoice_id is None
        ]

    def list_lines(self) -> list[InvoiceLine]:
        return list(self._lines.values())

    def list_by_contract(self, contract_id: UUID) -> list[InvoiceLine]:
        return [
            line for line in self._lines.values()
            if line.contract_id == contract_id
        ]

    def list_by_invoice(self, invoice_id: UUID) -> list[InvoiceLine]:
        return [
            line for line in self._lines.values()
            if line.invoice_id == invoice_id
        ]

    def update(self, invoice_line: InvoiceLine) -> None:
        self._lines[invoice_line.id] = invoice_line

    def exists(self, invoice_line_id: UUID) -> bool:
        return invoice_line_id in self._lines

    def delete_not_in_ids(
            self,
            invoice_id: UUID,
            keep_ids: set[UUID],
    ) -> int:
        to_delete = []

        for line_id, line in self._lines.items():
            if line.invoice_id != invoice_id:
                continue

            if keep_ids and line_id in keep_ids:
                continue

            to_delete.append(line_id)

        for line_id in to_delete:
            del self._lines[line_id]

        return len(to_delete)

    def get_for_assignment(self) -> list[InvoiceLine]:
        return [
            line for line in self._lines.values()
            if line.cost_node_id is None
               or line.cost_type_id is None
        ]

