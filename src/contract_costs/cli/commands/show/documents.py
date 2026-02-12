from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.printers.table_printer.excel_printer import ExcelPrinter
from contract_costs.cli.printers.table_printer.table_printer import TablePrinter
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.show_file_manager import FinancialRecordsShowFileManager
from contract_costs.services.documents.query.list_docuemnts_query_command import ListDocumentsQueryCommand
from contract_costs.services.documents.query.printer_columns.document_list_columns import document_list_columns
from contract_costs.services.documents.query.printer_columns.document_list_columns_excel import \
    document_list_columns_excel


def build_show_documents(subparsers):
    p = subparsers.add_parser(
        "documents",
        help="Show source documents",
    )

    p.add_argument(
        "--has-payload",
        action="store_true",
        help="Show only parsed documents",
    )

    p.add_argument(
        "--no-payload",
        action="store_true",
        help="Show only unparsed documents",
    )

    p.add_argument(
        "--has-record",
        action="store_true",
        help="Show only documents attached to financial record",
    )

    p.add_argument(
        "--no-record",
        action="store_true",
        help="Show only unattached documents",
    )

    p.add_argument(
        "--source",
        nargs="+",
        help="Filter by document source (e.g. ksef, pdf)",
    )

    p.add_argument(
        "--excel",
        action="store_true",
        help="Export documents list to Excel",
    )

    p.add_argument(
        "--last",
        type=int,
        help="Show last N documents",
    )

    p.set_defaults(handler=handle_show_documents)


REGISTRY.register_group("show", build_show_documents)





def handle_show_documents(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return None

    query_service = services.list_documents_query_service

    # -------------------------
    # FILTER LOGIC
    # -------------------------

    has_payload = None
    if args.has_payload:
        has_payload = True
    if args.no_payload:
        has_payload = False

    has_record = None
    if args.has_record:
        has_record = True
    if args.no_record:
        has_record = False

    # source — na razie single source per call
    source = args.source[0] if args.source else None

    cmd = ListDocumentsQueryCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        has_payload=has_payload,
        has_record=has_record,
        source=source,
    )

    result = query_service.execute(cmd)

    if not result:
        print("No documents found.")
        return None

    if args.last:
        result = result[:args.last]

    columns = document_list_columns()
    columns_excel = document_list_columns_excel()

    if args.excel:
        fm = FinancialRecordsShowFileManager(
            organization_id=organization_id,
            prefix="show_documents",
        )
        output_path = fm.create_output_file()
        printer: TablePrinter = ExcelPrinter(output_path=output_path)
        printer.print(
            organization_id=organization_id,
            items=result,
            columns=columns_excel,
            header=None,
        )
        print(f"Documents list exported to Excel: {output_path}")
        return None

    printer = CmdPrinter()
    printer.print(
        organization_id=organization_id,
        items=result,
        columns=columns,
        header=None,
    )

    return None
