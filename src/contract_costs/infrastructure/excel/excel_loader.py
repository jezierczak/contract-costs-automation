from pathlib import Path
from typing import Any
from openpyxl import load_workbook

from contract_costs.infrastructure.excel.excel_column import ExcelColumnType, ExcelColumn


class ExcelLoader[T]:
    @staticmethod
    def load(
        *,
        input_path: Path,
        columns: list[ExcelColumn[T]],
        sheet_name: str | None = None,
        start_row: int = 2,
    ) -> list[dict[str, Any]]:

        wb = load_workbook(input_path, data_only=True)
        ws = wb[sheet_name] if sheet_name else wb.active

        # Mapowanie: index kolumny -> ExcelColumn
        column_map: dict[int, ExcelColumn[T]] = {
            idx + 1: col
            for idx, col in enumerate(columns)
        }

        rows: list[dict[str, Any]] = []

        for row_idx in range(start_row, ws.max_row + 1):
            row_data: dict[str, Any] = {}
            empty_row = True

            for col_idx, col in column_map.items():
                cell = ws.cell(row=row_idx, column=col_idx)
                value = cell.value

                if value not in (None, ""):
                    empty_row = False

                # --- CHECKBOX ---
                if col.column_type == ExcelColumnType.CHECKBOX:
                    # Excel checkbox → True / False / None
                    value = bool(value) if value is not None else None

                # --- HIDDEN ---
                # hidden columns są normalnie czytane,
                # tylko nie są edytowalne w UI

                row_data[col.header] = value

            if not empty_row:
                rows.append(row_data)

        return rows
