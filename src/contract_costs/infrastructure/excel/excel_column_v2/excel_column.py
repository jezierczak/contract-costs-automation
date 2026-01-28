from dataclasses import dataclass
from typing import Callable, Any, TypeVar

from contract_costs.infrastructure.excel.excel_column_v2.dropdown_options import DropdownOptions
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column_v2.tree_options import TreeOptions

U = TypeVar("U")


@dataclass(frozen=True)
class ExcelColumn[T]:
    name: str
    header: str
    getter: Callable[[T], Any]

    column_type: ExcelColumnType = ExcelColumnType.DISPLAY
    editable: bool = False
    agg: bool = False

    dropdown: DropdownOptions | None = None
    tree: TreeOptions[T] | None = None

    @staticmethod
    def from_lists[U](
            *,
            headers: list[str],
            getters: list[Callable[[U], object]],
            types: list[ExcelColumnType] | None = None,
            editable: list[bool] | bool | None = None,
            dropdowns: list | None = None,
            tree: TreeOptions[U] | None = None,
            names: list[str] | None = None,
            agg: list[bool] | bool | None = None,
    ) -> list["ExcelColumn[U]"]:
        n = len(headers)

        def _norm_list(lst, default):
            if lst is None:
                return [default] * n
            if len(lst) != n:
                raise ValueError("All column lists must have the same length")
            return lst

        def _norm_bool_or_list(val, default) -> list[bool]:
            if val is None:
                return [default] * n
            if isinstance(val, bool):
                return [val] * n
            if len(val) != n:
                raise ValueError("All column lists must have the same length")
            return val

        types = _norm_list(types, ExcelColumnType.DISPLAY)
        editable = _norm_bool_or_list(editable, False)
        agg = _norm_bool_or_list(agg, False)
        dropdowns = _norm_list(dropdowns, None)
        names = _norm_list(names, None)

        columns: list[ExcelColumn[U]] = []

        for i in range(n):
            columns.append(
                ExcelColumn(
                    name=names[i] or headers[i].lower().replace(" ", "_"),
                    header=headers[i],
                    getter=getters[i],
                    column_type=types[i],
                    editable=editable[i],
                    agg=agg[i],
                    dropdown=dropdowns[i],
                    tree=tree if types[i] == ExcelColumnType.TREE else None,
                )
            )

        return columns

