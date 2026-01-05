# from pathlib import Path
# from uuid import UUID
#
# from openpyxl import load_workbook
#
# from contract_costs.services.invoices.actions.dto.invoice_apply_row import InvoiceApplyRow
#
#
# class InvoiceApplyExcelLoader:
#     @staticmethod
#     def load( path: Path) -> list[InvoiceApplyRow]:
#         wb = load_workbook(path)
#         ws = wb.active
#
#         rows: list[InvoiceApplyRow] = []
#
#         for row in ws.iter_rows(min_row=2):
#             selected_cell = row[0].value
#             invoice_id_cell = row[1].value  # zakładamy ID w kolumnie B
#
#             if not invoice_id_cell:
#                 continue
#
#             rows.append(
#                 InvoiceApplyRow(
#                     invoice_id=UUID(str(invoice_id_cell)),
#                     selected=str(selected_cell).strip().lower() == "x",
#                 )
#             )
#
#         return rows