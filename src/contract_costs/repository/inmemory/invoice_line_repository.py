from datetime import date, datetime
from uuid import UUID
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository


class InMemoryInvoiceLineRepository(InvoiceLineRepository):

    def __init__(self) -> None:
        self._lines: dict[UUID, InvoiceLine] = {}
        self._created_at: dict[UUID, datetime] = {}

    def add(
        self,
        invoice_line: InvoiceLine,
        *,
        created_at: datetime | None = None,
    ) -> None:
        self._lines[invoice_line.id] = invoice_line
        self._created_at[invoice_line.id] = created_at or datetime.now()

    # 🔥 HOOK TYLKO DO TESTÓW
    def _add_with_created_at(
            self,
            invoice_line: InvoiceLine,
            created_at: datetime,
    ) -> None:
        self._lines[invoice_line.id] = invoice_line
        self._created_at[invoice_line.id] = created_at

    def get(self, invoice_line_id: UUID) -> InvoiceLine | None:
        return self._lines.get(invoice_line_id)

    def list_by_invoice_ids(self, invoice_ids: list[UUID]) -> list[InvoiceLine]:
        return [
            line
            for id_ in invoice_ids
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
            if line.contract_node_id is None
               or line.value_type_id is None
        ]

    def list_by_contract_until(
            self,
            *,
            contract_id: UUID,
            snapshot_date: date,
    ) -> list[InvoiceLine]:

        cutoff = datetime.combine(snapshot_date, datetime.max.time())

        result = []
        for line_id, line in self._lines.items():
            created_at = self._created_at.get(line_id)

            if line.contract_id != contract_id:
                continue

            if created_at is None:
                continue

            if created_at <= cutoff:
                result.append(line)

        return result
