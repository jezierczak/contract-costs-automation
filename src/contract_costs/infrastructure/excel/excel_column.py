from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any

from contract_costs.infrastructure.excel.base_excel_column import BaseExcelColumn
from contract_costs.infrastructure.excel.excel_column_type import ExcelColumnType


@dataclass(frozen=True)
class ExcelColumn[T](BaseExcelColumn):
    header: str
    getter: Callable[[T], Any]
    column_type: ExcelColumnType = ExcelColumnType.DISPLAY
    editable: bool = False
    options: list[str] | None = None