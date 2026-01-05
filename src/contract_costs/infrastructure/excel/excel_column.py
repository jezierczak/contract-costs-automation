from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any

class ExcelColumnType(Enum):
    DISPLAY = "display"
    CHECKBOX = "checkbox"
    HIDDEN = "hidden"

@dataclass(frozen=True)
class ExcelColumn[T]:
    header: str
    getter: Callable[[T], Any]
    column_type: ExcelColumnType = ExcelColumnType.DISPLAY
    editable: bool = False