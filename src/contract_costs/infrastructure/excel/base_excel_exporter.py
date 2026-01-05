from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Protection, Alignment
from openpyxl.utils import get_column_letter

from contract_costs.infrastructure.excel.excel_column import ExcelColumn, ExcelColumnType
from contract_costs.infrastructure.excel.excel_common_methods import ExcelCommonMethods


class BaseExcelExporter[T]:

    @staticmethod
    def export(
        *,
        items: list[T],
        columns: list[ExcelColumn[T]],
        output_path: Path,
        sheet_name: str = "data",
    ) -> None:

        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name

        # ======================
        # HEADER
        # ======================
        ws.append([col.header for col in columns])

        # ======================
        # ROWS
        # ======================
        for item in items:
            row = []
            for col in columns:
                try:
                    value = col.getter(item)
                except Exception as e:
                    raise RuntimeError(
                        f"Error while exporting column '{col.header}'"
                    ) from e

                # CHECKBOX → Excel oczekuje bool
                if col.column_type == ExcelColumnType.CHECKBOX:
                    value = "☑" if value else "☐"

                row.append(value)

            ws.append(row)

        # ======================
        # COLUMN METADATA
        # ======================
        for idx, col in enumerate(columns, start=1):
            col_letter = get_column_letter(idx)

            # --- HIDDEN ---
            if col.column_type == ExcelColumnType.HIDDEN:
                ws.column_dimensions[col_letter].hidden = True

            # --- PROTECTION ---
            for row in ws.iter_rows(
                min_col=idx,
                max_col=idx,
                min_row=2,
                max_row=ws.max_row,
            ):
                cell = row[0]

                # editable = False → lock cell
                if not col.editable:
                    cell.protection = Protection(locked=True)
                else:
                    cell.protection = Protection(locked=False)

        # ======================
        # SHEET PROTECTION
        # ======================
        ws.protection.enable()
        for ws in wb.worksheets:
            ExcelCommonMethods.style_header(ws)
            ExcelCommonMethods.autosize_columns(ws)


            ExcelCommonMethods.freeze_header(ws)
            # ExcelCommonMethods.apply_autofilter(ws)
            ExcelCommonMethods.zebra_rows(ws)

        for cell in ws["A"]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions["A"].width = 6

        wb.save(output_path)

