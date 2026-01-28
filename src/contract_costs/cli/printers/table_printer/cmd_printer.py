import shutil
from decimal import Decimal
from typing import Any

from contract_costs.cli.printers.table_printer.table_printer import TablePrinter
from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column_v2.tree_options import TreeOptions


class CmdPrinter[T](TablePrinter[T]):
    def __init__(self, *, style: str = "classic"):
        self._style = style
    # =========================================================
    # PUBLIC API
    # =========================================================

    def print(
        self,
        *,
        items: list[T],
        columns: list[ExcelColumn[T]],
        header: dict[str, list[str]] | None = None,
    ) -> None:

        print()

        # ===== HEADER (META) =====
        if header:
            for key, values in header.items():
                print(f"{key}: {' | '.join([value for value in values if value])}")
            print()

        tree_col_idx = next(
            (i for i, c in enumerate(columns)
             if c.column_type == ExcelColumnType.TREE),
            None,
        )

        # ===== COLLECT RAW ROWS =====
        if tree_col_idx is None:
            raw_rows = self._collect_flat_rows(items, columns)
        else:
            raw_rows = self._collect_tree_rows(items, columns, tree_col_idx)

        # ===== AGGREGATION =====
        if any(col.agg for col in columns):
            agg_row = self._aggregate_rows(raw_rows, columns)
            raw_rows.append(agg_row)

        # ===== FORMAT =====
        rows = self._format_rows(raw_rows, columns)

        # ===== PRINT =====
        self._print_table(columns, rows)

    # =========================================================
    # COLLECT RAW ROWS
    # =========================================================

    @staticmethod
    def _collect_flat_rows(
        items: list[T],
        columns: list[ExcelColumn[T]],
    ) -> list[list[Any]]:
        return [
            [col.getter(item) for col in columns]
            for item in items
        ]

    @staticmethod
    def _collect_tree_rows(
        items: list[T],
        columns: list[ExcelColumn[T]],
        tree_col_idx: int,
    ) -> list[list[Any]]:

        tree:TreeOptions[T] | None = columns[tree_col_idx].tree
        if tree is None:
            raise RuntimeError("TREE column requires TreeOptions")

        children: dict[object | None, list[T]] = {}
        for item in items:
            pid = tree.parent_id(item)
            children.setdefault(pid, []).append(item)

        if tree.sort_key:
            for lst in children.values():
                lst.sort(key=tree.sort_key)

        rows: list[list[Any]] = []

        def walk(parent_id, prefix: str):
            nodes = children.get(parent_id, [])

            for idx, item in enumerate(nodes):
                last = idx == len(nodes) - 1
                connector = "└── " if last else "├── "
                extension = "    " if last else "│   "

                row: list[Any] = []

                for col_idx, col in enumerate(columns):
                    if col_idx == tree_col_idx:
                        label = (
                            connector + str(col.getter(item))
                            if parent_id is None
                            else prefix + connector + str(col.getter(item))
                        )
                        row.append(label)
                    else:
                        row.append(col.getter(item))

                rows.append(row)
                walk(tree.id(item), prefix + extension)

        walk(None, "")
        return rows

    # =========================================================
    # AGGREGATION
    # =========================================================

    @staticmethod
    def _aggregate_rows(
        rows: list[list[Any]],
        columns: list[ExcelColumn],
    ) -> list[Any]:

        result: list[Any] = []

        for idx, col in enumerate(columns):
            if col.column_type == ExcelColumnType.TREE:
                result.append("SUM")
                continue

            if not col.agg:
                result.append(None)
                continue

            total = Decimal("0")

            for row in rows:
                val = row[idx]
                if isinstance(val, (int, float, Decimal)):
                    total += Decimal(val)

            result.append(total)

        return result

    # =========================================================
    # FORMAT
    # =========================================================

    @staticmethod
    def _format_rows(
        rows: list[list[Any]],
        columns: list[ExcelColumn],
    ) -> list[list[str]]:

        formatted: list[list[str]] = []

        for row in rows:
            out_row: list[str] = []
            for val, col in zip(row, columns):
                out_row.append(
                    CmdPrinter._format_value(val, col.column_type)
                )
            formatted.append(out_row)

        return formatted

    @staticmethod
    def _format_value(value: Any, col_type: ExcelColumnType) -> str:
        if value is None:
            return ""

        if col_type == ExcelColumnType.PERCENT:
            if isinstance(value, (Decimal, float, int)):
                return f"{(Decimal(value) * 100):.1f}%"
            return str(value)

        if col_type in (
            ExcelColumnType.DISPLAY,
            ExcelColumnType.LINK,
            ExcelColumnType.FOLDER,
        ):
            if isinstance(value, (Decimal, float, int)):
                return f"{Decimal(value):,.2f}".replace(",", " ").replace(".", ",")
            return str(value)

        if col_type == ExcelColumnType.CHECKBOX:
            return "YES" if value else "NO"

        # TREE / HIDDEN / fallback
        return str(value)

    # =========================================================
    # PRINT TABLE
    # =========================================================
    def _print_table(
        self,
        columns: list[ExcelColumn],
        rows: list[list[str]],
    ) -> None:

        if not rows:
            return

        if self._style == "pipe":
            self._print_pipe_table(columns, rows)
        else:
            self._print_classic_table(columns, rows)


    def _print_classic_table(
        self,
        columns: list[ExcelColumn],
        rows: list[list[str]],
    ) -> None:

        if not rows:
            return

        col_count = len(columns)

        # --- widths ---
        widths: list[int] = []
        for i in range(col_count):
            max_width = max(len(row[i]) for row in rows)
            max_width = max(max_width, len(columns[i].header))
            widths.append(max_width)

        # --- AUTO FIT TO TERMINAL ---
        term_width = self.terminal_width()

        widths = self.fit_widths_to_terminal(
            widths=widths,
            columns=columns,
            max_width=term_width,
        )

        total_width = sum(widths) + 2 * (len(widths) - 1)

        # --- header ---
        header_row = "  ".join(
            columns[i].header.ljust(widths[i])
            for i in range(col_count)
        )

        print("-" * total_width)
        print(header_row)
        print("-" * total_width)

        # --- body ---
        for row in rows:
            line = "  ".join(
                CmdPrinter.clip(row[i], widths[i]).rjust(widths[i])
                if CmdPrinter._is_numeric(row[i])
                else CmdPrinter.clip(row[i], widths[i]).ljust(widths[i])
                for i in range(col_count)
            )
            print(line)

    def _print_pipe_table(
        self,
        columns: list[ExcelColumn],
        rows: list[list[str]],
    ) -> None:

        col_count = len(columns)

        widths: list[int] = []
        for i in range(col_count):
            max_width = max(len(row[i]) for row in rows)
            max_width = max(max_width, len(columns[i].header))
            widths.append(max_width)

        # --- AUTO FIT TO TERMINAL ---
        term_width = self.terminal_width()

        widths = self.fit_widths_to_terminal(
            widths=widths,
            columns=columns,
            max_width=term_width,
        )

        def row_line(values: list[str]) -> str:
            return " | ".join(
                (
                    CmdPrinter.clip(values[i], widths[i]).rjust(widths[i])
                    if CmdPrinter._is_numeric(values[i])
                    else CmdPrinter.clip(values[i], widths[i]).ljust(widths[i])
                )
                for i in range(col_count)
            )

        def sep_upper() -> str:
            return "-" * len(row_line([c.header for c in columns]))
        def sep() -> str:
            return row_line(["-" * w for w in widths]).replace("|", "+")


        print(sep_upper())
        print(row_line([c.header for c in columns]))
        print(sep())

        for row in rows:
            print(row_line(row))


    @staticmethod
    def _is_numeric(value: str) -> bool:
        value = value.replace(" ", "").replace(",", "").replace("%", "")
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def terminal_width(default: int = 120) -> int:
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return default

    @staticmethod
    def table_total_width(
            widths: list[int],
            *,
            separator_width: int,
    ) -> int:
        return sum(widths) + separator_width * (len(widths) - 1)


    def fit_widths_to_terminal(
            self,
            *,
            widths: list[int],
            columns: list[ExcelColumn],
            max_width: int,
            min_text_width: int = 10,
    ) -> list[int]:

        separator_width = 3 if self._style == "pipe" else 2
        total = self.table_total_width(widths, separator_width=separator_width)
        if total <= max_width:
            return widths

        overflow = total - max_width

        # kolumny tekstowe do przycinania
        shrinkable = [
            i for i, col in enumerate(columns)
            if col.column_type == ExcelColumnType.DISPLAY
        ]

        widths = widths[:]  # kopia

        while overflow > 0 and shrinkable:
            for i in shrinkable:
                if widths[i] > min_text_width:
                    widths[i] -= 1
                    overflow -= 1
                    if overflow <= 0:
                        break
            else:
                break  # nie da się już ciąć

        return widths

    @staticmethod
    def clip(value: str, width: int) -> str:
        if len(value) <= width:
            return value
        if width <= 1:
            return value[:width]
        return value[: width - 1] + "…"
