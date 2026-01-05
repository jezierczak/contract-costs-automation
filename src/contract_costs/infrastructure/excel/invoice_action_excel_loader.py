from pathlib import Path
from uuid import UUID

from openpyxl import load_workbook

from contract_costs.services.invoices.actions.dto.invoice_action_command import InvoiceActionCommand, InvoiceSelector, \
    InvoiceAction


class InvoiceActionExcelLoader:
    @staticmethod
    def load_to_accountant( path: Path) -> InvoiceActionCommand:
        wb = load_workbook(path)
        ws = wb.active

        selectors: list[InvoiceSelector] = []

        for row in ws.iter_rows(min_row=2):
            selected = str(row[0].value).strip().lower() == "x"
            invoice_id = row[1].value

            if not selected or not invoice_id:
                continue

            selectors.append(
                InvoiceSelector(invoice_id=UUID(str(invoice_id)))
            )

        return InvoiceActionCommand(
            action=InvoiceAction.MARK_SENT_TO_ACCOUNTANT,
            selectors=selectors,
            payload=None,
        )

    @staticmethod
    def set_paid(path: Path) -> InvoiceActionCommand:
        wb = load_workbook(path)
        ws = wb.active

        selectors: list[InvoiceSelector] = []

        for row in ws.iter_rows(min_row=2):
            selected = str(row[0].value).strip().lower() == "x"
            invoice_id = row[1].value

            if not selected or not invoice_id:
                continue

            selectors.append(
                InvoiceSelector(invoice_id=UUID(str(invoice_id)))
            )

        return InvoiceActionCommand(
            action=InvoiceAction.MARK_PAID,
            selectors=selectors,
            payload=None,
        )