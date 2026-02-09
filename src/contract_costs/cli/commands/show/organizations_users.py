from contract_costs.cli.context import get_services
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType

def build_show_organization_users(subparsers):
    p = subparsers.add_parser("organization", help="Show organizations")
    sub = p.add_subparsers(dest="entity", required=True)
    u = sub.add_parser("users", help="Show organization users")
    u.set_defaults(handler=handle_show_organization_users)

REGISTRY.register_group("show", build_show_organization_users)


def handle_show_organization_users(args):
    services = get_services()
    try:
        org_id = require_organization_id(services.context)
    except ContextError:
        return
    users = services.show_organization_users.execute(org_id)
    organization = services.organization_repository.get(org_id)
    header = {
        "Users for organization": [organization.code, organization.name],
    }

    def user_status(u):
        if not u.is_active:
            return "inactive"
        if u.accepted_at is None:
            return "invited"
        return "active"

    columns = ExcelColumn.from_lists(
        headers=["LOGIN","ROLE","STATUS","NAME"],
        getters=[lambda i: i.login,
                 lambda i: i.role.value,
                 user_status,
                 lambda i: i.full_name
                 ],
        types=[ExcelColumnType.DISPLAY, ExcelColumnType.DISPLAY,ExcelColumnType.DISPLAY,ExcelColumnType.DISPLAY],
    )

    printer = CmdPrinter()
    printer.print(
        items=users,
        columns=columns,
        header=header,
    )

