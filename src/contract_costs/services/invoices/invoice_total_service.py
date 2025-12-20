from decimal import Decimal
from uuid import UUID

from contract_costs.model.invoice_totals import InvoiceTotals
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository


class InvoiceTotalsService:

    def __init__(self, invoice_line_repo: InvoiceLineRepository) -> None:
        self._invoice_line_repo = invoice_line_repo

    def calculate(self, invoice_id: UUID) -> InvoiceTotals:
        lines = self._invoice_line_repo.list_by_invoice(invoice_id)

        net = sum(
            (line.amount.net or Decimal("0.00") for line in lines),
            Decimal("0.00"),
        )
        tax = sum(
            (line.amount.tax for line in lines),
            Decimal("0.00"),
        )
        gross = sum(
            (line.amount.gross for line in lines),
            Decimal("0.00"),
        )

        return InvoiceTotals(
            invoice_id=invoice_id,
            net=net,
            tax=tax,
            gross=gross,
        )
