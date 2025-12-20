from dataclasses import replace
from uuid import uuid4, UUID

from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.services.invoices.dto.common import InvoiceLineUpdate, InvoiceRef


class InvoiceLineUpdateService:
    """
    Odpowiada za:
    - tworzenie linii faktur
    - aktualizację linii faktur
    - koszty bez faktury
    """

    def __init__(self, invoice_line_repository: InvoiceLineRepository) -> None:
        self._invoice_line_repository = invoice_line_repository

    def apply(
        self,
        lines: list[InvoiceLineUpdate],
        ref_map: dict[str, UUID],
    ) -> None:
        for update in lines:
            invoice_id = self._resolve_invoice_id(update.invoice_ref, ref_map)

            if update.invoice_line_id is None:
                self._create_line(update, invoice_id)
            else:
                self._update_line(update, invoice_id)

    def _create_line(
        self,
        update: InvoiceLineUpdate,
        invoice_id: UUID | None,
    ) -> None:
        line = InvoiceLine(
            id=uuid4(),
            invoice_id=invoice_id,  # 🔥 TU JEST RÓŻNICA
            description=update.description,
            quantity=update.quantity,
            unit=update.unit,
            amount=update.amount,
            contract_id=update.contract_id,
            cost_node_id=update.cost_node_id,
            cost_type_id=update.cost_type_id,
        )
        self._invoice_line_repository.add(line)

    def _update_line(
        self,
        update: InvoiceLineUpdate,
        invoice_id: UUID | None,
    ) -> None:
        line = self._invoice_line_repository.get(update.invoice_line_id)
        if line is None:
            raise ValueError("Invoice line not found")

        updated = replace(
            line,
            invoice_id=invoice_id,  # 🔥 TU JEST RÓŻNICA
            description=update.description,
            quantity=update.quantity,
            unit=update.unit,
            amount=update.amount,
            contract_id=update.contract_id,
            cost_node_id=update.cost_node_id,
            cost_type_id=update.cost_type_id,
        )

        self._invoice_line_repository.update(updated)

    @staticmethod
    def _resolve_invoice_id(
        ref: InvoiceRef | None,
        ref_map: dict[str, UUID],
    ) -> UUID | None:
        """
        Rozwiązuje invoice_id na podstawie:
        - None → koszt bez faktury
        - invoice_id → istniejąca faktura
        - external_ref → nowa faktura z Excela
        """
        if ref is None:
            return None

        if ref.invoice_id is not None:
            return ref.invoice_id

        if ref.external_ref is not None:
            if ref.external_ref not in ref_map:
                raise ValueError(
                    f"Invoice external_ref not found: {ref.external_ref}"
                )
            return ref_map[ref.external_ref]

        raise ValueError("Invalid InvoiceRef")
