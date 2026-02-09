from pathlib import Path
from uuid import UUID

from openpyxl import load_workbook

from contract_costs.infrastructure.excel.invoice_excel_context import FinancialRecordExcelContext, EXCEL_SPECS
from contract_costs.services.financial_records.actions.dto.invoice_action_command import FinancialRecordActionCommand, FinancialRecordSelector, \
     financial_record_action_from_excel


class FinancialRecordActionExcelLoader:


    @staticmethod
    def load(
            path: Path,
            *,
            context: FinancialRecordExcelContext,
    ) -> list[FinancialRecordActionCommand]:

        spec = EXCEL_SPECS[context]

        wb = load_workbook(path)
        ws = wb.active
        if ws is None:
            raise ValueError(f"No active worksheet in Excel file: {path}")
        grouped: dict[str, list[FinancialRecordSelector]] = {}

        for row in ws.iter_rows(min_row=2):

            raw_action = row[spec.action_column].value
            invoice_id = row[spec.record_id_column].value

            if not raw_action or not invoice_id:
                continue

            raw_action = str(raw_action).strip().lower()
            # print(raw_action, spec.allowed_actions)
            if raw_action not in spec.allowed_actions:
                continue

                # raise ValueError(
                #     f"Action '{raw_action}' not allowed in {context.value} excel"
                # )

            grouped.setdefault(raw_action, []).append(
                FinancialRecordSelector(record_id=UUID(str(invoice_id)))
            )

        return [
            FinancialRecordActionCommand(
                action=financial_record_action_from_excel(
                    context=context,
                    raw=raw_action,
                ),
                selectors=selectors,
                payload=None,
            )
            for raw_action, selectors in grouped.items()
        ]
