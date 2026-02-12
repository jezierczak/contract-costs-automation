from dataclasses import dataclass
from typing import Callable, Any

from contract_costs.infrastructure.excel.excel_column_type import ExcelColumnType


@dataclass(frozen=True)
class BaseExcelColumn[T]:
    header: str
    getter: Callable[[T], Any]
    column_type: ExcelColumnType = ExcelColumnType.DISPLAY
    editable: bool = False