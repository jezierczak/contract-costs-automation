from pathlib import Path

from contract_costs.cli.printers.table_printer.table_printer import TablePrinter
from contract_costs.infrastructure.excel.excel_column_v2.base_excel_exporter_v2 import BaseExcelExporterV2
from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn


class ExcelPrinter[T](TablePrinter[T]):

    def __init__(self, output_path: Path):
        self._exporter = BaseExcelExporterV2[T]()
        self._output_path = output_path

    def print(
        self,
        *,
        items: list[T],
        columns: list[ExcelColumn[T]],
        header: dict[str, list[str]] | None = None,
    ) -> None:
        self._exporter.add_sheet(
            items=items,
            columns=columns,
            header=header,
            sheet_name="data",
        )
        self._exporter.save(self._output_path)
