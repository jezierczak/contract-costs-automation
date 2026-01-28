import logging
from datetime import datetime, date
from uuid import UUID

from contract_costs.cli.context import get_services
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.printers.table_printer.excel_printer import ExcelPrinter
from contract_costs.cli.printers.table_printer.table_printer import TablePrinter
from contract_costs.cli.registry import REGISTRY

# from contract_costs.infrastructure.excel.contracts.contract_cost_node_tree_excel_exporter import \
#     ContractTreeExcelExporter
from contract_costs.infrastructure.filesystem.show_file_manager import ContractsShowFileManager
from contract_costs.reports.contracts.contract_list_columns import contract_list_columns
from contract_costs.reports.contracts.contract_node_tree_column import contract_node_tree_columns

logger = logging.getLogger(__name__)


def build_show_contracts(subparsers):
    p = subparsers.add_parser(
        "contracts",
        help="Show contracts",
    )

    p.add_argument(
        "ref",
        nargs="?",
        help="Contract UUID or code",
    )

    p.add_argument(
        "--excel",
        action="store_true",
        help="Export contracts list or contract tree to Excel (read-only)",
    )

    p.add_argument(
        "--active",
        action="store_true",
        help="Show only active contracts",
    )
    p.add_argument(
        "--at-date",
        help="Show contract state at given date (YYYY-MM-DD)",
    )

    p.set_defaults(handler=handle_show_contracts)

REGISTRY.register_group("show", build_show_contracts)


def handle_show_contracts(args) -> None:
    services = get_services()
    query = services.contract_query_service

    if args.ref:
        return _handle_show_single_contract(args, query,services.contract_repository)

    items = query.list_contracts()

    if args.active:
        items = [c for c in items if c.is_active]

    if not items:
        print("No contracts found.")
        return None

    columns = contract_list_columns()
    header = {
            "Report": ["Contracts list"],
            "Active only": ["YES"] if args.active else ["NO"],
            "Generated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        }

    if args.excel:
        fm = ContractsShowFileManager(contract_code="contract_list")
        output_path = fm.create_output_file()
        printer: TablePrinter = ExcelPrinter(output_path=output_path)
        printer.print(
            items=items,
            columns=columns,
            header=header,
        )
        print(f"Invoice list exported to Excel: {output_path}")
        return None

    printer = CmdPrinter()
    printer.print(
        items=items,
        columns=columns,
        header=header,
    )

    return None


def _handle_show_single_contract(args, query,repo) -> None:
    contract = query.get_contract_details(
        contract_id=_resolve_contract_id(args.ref, repo),
        at_date=date.fromisoformat(args.at_date) if args.at_date else None,
    )

    header = {
        "Contract": [contract.code],
        "Name": [contract.name],
        "Description": [contract.description],
        "Status": [contract.status],
        "Start date": [str(contract.start_date) if contract.start_date else "-"],
        "End date": [str(contract.end_date) if contract.end_date else "-"],
        "Generated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    }

    columns = contract_node_tree_columns()

    if args.excel:
        fm = ContractsShowFileManager(contract_code=contract.code)
        output_path = fm.create_output_file()
        printer: TablePrinter = ExcelPrinter(output_path=output_path)
        printer.print(
            items=contract.nodes,
            columns=columns,
            header=header,
        )
        print(f"Invoice list exported to Excel: {output_path}")
        return

    printer = CmdPrinter()
    printer.print(
        items=contract.nodes,
        columns=columns,
        header=header,
    )


def _resolve_contract_id(ref: str, repo) -> UUID:
    try:
        return UUID(ref)
    except ValueError:
        contract = repo.get_by_code(ref)
        if not contract:
            raise ValueError(f"No contract found for ref: {ref}")
        return contract.id
# def handle_show_contracts(args) -> None:
#     services = get_services()
#     repo = services.contract_repository
#     node_repo = services.contract_node_repository
#
#     # ---------- SINGLE CONTRACT ----------
#     if args.ref:
#         contract = _resolve_contract(args.ref, repo)
#         if not contract:
#             print(f"No contract found for ref: {args.ref}")
#             return
#
#         if args.excel:
#             exporter = ContractTreeExcelExporter()
#
#             fm = ContractsShowFileManager(contract_code=contract.code)
#             output_path = fm.create_output_file()
#
#             exporter.export(
#                 contract=contract,
#                 cost_nodes=node_repo.list_by_contract(contract.id),
#                 output_path=output_path,
#             )
#             print(f"Contract tree exported to Excel: {output_path}")
#             return
#
#         print("Contract details:")
#         print(f"ID:        {contract.id}")
#         print(f"Code:      {contract.code}")
#         print(f"Name:      {contract.name}")
#         print(f"Active:    {contract.status.value}")
#         print(f"Start:     {contract.start_date}")
#         print(f"End:       {contract.end_date}")
#
#         nodes = node_repo.list_by_contract(contract.id)
#         tree = ContractNodeTreeIndex(nodes)
#
#         print_contract_node_tree(
#             tree=tree,
#         )
#
#         print("- " * 23)
#         return
#
#     # ---------- LIST CONTRACTS ----------
#     contracts = repo.list()
#
#     if args.active:
#         contracts = [c for c in contracts if c.is_active]
#
#     if not contracts:
#         print("No contracts found.")
#         return
#
#     print(f"{'CODE':<12} {'NAME':<30} {'STATUS'}")
#     print("-" * 55)
#
#     for c in contracts:
#         print(
#             f"{c.code:<12} "
#             f"{(c.name or ''):<30} "
#             f"{ c.status.value}"
#         )
#
# # ---------- utils ----------
#
# def _resolve_contract(ref: str, repo) -> Contract | None:
#     try:
#         contract = repo.get(UUID(ref))
#         if contract:
#             return contract
#     except ValueError:
#         pass
#
#     contract = repo.get_by_code(ref)
#     # if contract:
#     return contract
#
#
# REGISTRY.register_group("show", build_show_contracts)
#
# def print_contract_node_tree(
#     *,
#     tree: ContractNodeTreeIndex,
#     parent_id: UUID | None = None,
#     prefix: str = "",
# ) -> None:
#     if parent_id is None:
#         children = tree.roots()
#     else:
#         children = tree.children_of(parent_id)
#     nodes_by_parent = tree.children_by_parent  # lokalny wyjątek
#
#     for index, node in enumerate(children):
#         last = index == len(children) - 1
#
#         connector = "└── " if last else "├── "
#         status = "" if node.is_active else " [INACTIVE]"
#
#         calc_budget = ContractNode.calculate_budget_from_leaves(
#             node.id,
#             nodes_by_parent,
#         )
#
#         print(
#             f"{prefix}{connector}{node.code} – {node.name}{status}  {calc_budget}"
#         )
#
#         extension = "    " if last else "│   "
#
#         print_contract_node_tree(
#             tree=tree,
#             parent_id=node.id,
#             prefix=prefix + extension,
#         )
#

