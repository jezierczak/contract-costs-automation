import logging
from datetime import datetime, date
from uuid import UUID

from contract_costs.cli.context import get_services
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.printers.table_printer.excel_printer import ExcelPrinter
from contract_costs.cli.printers.table_printer.table_printer import TablePrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError


from contract_costs.infrastructure.filesystem.show_file_manager import ContractsShowFileManager
from contract_costs.model.contract import ContractType
from contract_costs.reports.contracts.contract_list_columns import contract_list_columns
from contract_costs.reports.contracts.contract_node_tree_column import contract_node_tree_columns
from contract_costs.services.contracts.query.contract_details.contract_details_query_command import ContractDetailsQuery
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery

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
        "--system",
        action="store_true",
        help="Show only system contracts attached to owners companies",
    )

    p.add_argument(
        "--at-date",
        help="Show contract state at given date (YYYY-MM-DD)",
    )

    p.set_defaults(handler=handle_show_contracts)

REGISTRY.register_group("show", build_show_contracts)


def handle_show_contracts(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return None

    if args.ref:
        return _handle_show_single_contract(
            args,
            organization_id,
            actor_user_id,
            services
        )
    contract_type = ContractType.PROJECT
    if args.system:
        contract_type = ContractType.SYSTEM

    items = services.action_bus.execute(
        action=ListContractsQuery(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            contract_type=contract_type,
        ),
        handler=services.list_contracts_service,
    )

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
        fm = ContractsShowFileManager(
            organization_id=organization_id,
            contract_code="contract_list")
        output_path = fm.create_output_file()
        printer: TablePrinter = ExcelPrinter(output_path=output_path)
        printer.print(
            organization_id=str(organization_id),
            items=items,
            columns=columns,
            header=header,
        )
        print(f"Contracts list exported to Excel: {output_path}")

        return None

    printer = CmdPrinter()
    printer.print(
        organization_id=str(organization_id),
        items=items,
        columns=columns,
        header=header,
    )

    return None


def _handle_show_single_contract(args, organization_id, actor_user_id, services) -> None:
    contract = services.action_bus.execute(
        action=ContractDetailsQuery(
            organization_id=organization_id,
            contract_id=_resolve_contract_id(args.ref,services.contract_repository,organization_id),
            actor_user_id=actor_user_id,
            at_date=date.fromisoformat(args.at_date) if args.at_date else None
        ),
        handler=services.contract_details_service,
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
        fm = ContractsShowFileManager(
            organization_id=organization_id,
            contract_code=contract.code)
        output_path = fm.create_output_file()
        printer: TablePrinter = ExcelPrinter(output_path=output_path)
        printer.print(
            organization_id=organization_id,
            items=contract.nodes,
            columns=columns,
            header=header,
        )
        print(f"Contract '{contract.code}' exported to Excel: {output_path}")

        return

    printer = CmdPrinter()
    printer.print(
        organization_id=organization_id,
        items=contract.nodes,
        columns=columns,
        header=header,
    )


def _resolve_contract_id(ref: str, repo,organization_id) -> UUID:
    try:
        return UUID(ref)
    except ValueError:
        contract = repo.get_by_code(
            organization_id=organization_id,
            contract_code=ref,
        )
        if not contract:
            raise ValueError(f"No contract found for ref: {ref}")
        return contract.id
