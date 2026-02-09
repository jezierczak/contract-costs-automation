from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.printers.table_printer.table_printer import TablePrinter
from contract_costs.reports.value_types.value_type_columns import value_type_list_columns
from contract_costs.services.value_types.query.dto.value_type_dto import ValueTypeDTO


class ValueTypePrinter:

    @staticmethod
    def print(items,organization_id) -> None:
        printer:TablePrinter[ValueTypeDTO] = CmdPrinter()
        printer.print(
            organization_id=organization_id,
            items=items,
            columns=value_type_list_columns(),
            header={
                "Value types": [f"count = {len(items)}"]
            },
        )