from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn


class TablePrinter[T]:
    def print(
        self,
        *,
        items: list[T],
        columns: list[ExcelColumn[T]],
        header: dict[str, list[str]] | None = None,
    ) -> None:
        ...
