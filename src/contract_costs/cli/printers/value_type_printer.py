from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.reports.value_types.value_type_columns import value_type_list_columns
from contract_costs.services.value_types.query.dto.value_type_dto import ValueTypeDTO


class ValueTypePrinter:

    # @staticmethod
    # def print(items: list[ValueTypeDTO]) -> None:
    #     if not items:
    #         print("No value types found.")
    #         return
    #     # =====================
    #     # HEADER
    #     # =====================
    #     header = f"[{'CODE':^12}] {'NAME':<40} {'DIRECTION':<12} DESCRIPTION"
    #     print(header)
    #     print("-" * len(header))
    #     # =====================
    #     # ROWS
    #     # =====================
    #     items = sorted(items, key=lambda x: (not x.is_active,x.direction, x.code))
    #     for ct in items:
    #         line = f"[{ct.code:^12}] {ct.name:<40} {ct.direction:<12} {ct.description}"
    #
    #         if not ct.is_active:
    #             line += "  (inactive)"
    #
    #         print(line)
    #
    @staticmethod
    def print(items) -> None:
        printer = CmdPrinter()
        printer.print(
            items=items,
            columns=value_type_list_columns(),
            header={
                "Value types": [f"count = {len(items)}"]
            },
        )