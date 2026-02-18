import logging
from itertools import chain

from contract_costs.cli.commands.header_builder.invoice_report_header_builder import FinancialRecordReportHeaderBuilder
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.printers.table_printer.table_printer import TablePrinter
from contract_costs.cli.printers.table_printer.excel_printer import ExcelPrinter
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.show_file_manager import  FinancialRecordsShowFileManager

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.model.financial_record import FinancialRecordStatus, PaymentStatus
from contract_costs.model.value_direction import ValueDirection
from contract_costs.reports.invoices.invoice_list_columns import financial_record_list_columns, financial_record_list_columns_excel
from contract_costs.services.financial_records.review.dto.financial_record_review_query import FinancialRecordReviewQuery

logger = logging.getLogger(__name__)


def build_show_financial_records(subparsers):
    p = subparsers.add_parser(
        "records",
        help="Show financial records",
    )
    p.add_argument("--buyer-nip",
                   nargs="+",
                   help="Filter by buyer NIP")
    p.add_argument("--buyer-name",
                   nargs="+",
                   help="Filter by buyer Name")
    p.add_argument("--buyer-role",
                   nargs="+",
                   help="Filter by buyer Role")
    p.add_argument("--buyer", help="Filter by buyer")

    p.add_argument("--seller-nip",
                   nargs="+",
                   help="Filter by seller NIP(s)")
    p.add_argument("--seller-name",
                   nargs="+",
                   help="Filter by seller Name")

    p.add_argument("--seller-role",
                   nargs="+",
                   help="Filter by seller Role")
    p.add_argument("--seller", help="Filter by seller")

    p.add_argument(
        "--status",
        nargs="+",
        choices=["NEW", "IN_PROGRESS", "PROCESSED", "DELETED"],
        help="Filter by financial record status",
    )
    p.add_argument(
        "--unpaid",
        action="store_true",
        help="Show only unpaid financial records",
    )

    p.add_argument(
        "--direction",
        choices=["COST", "REVENUE", "INTERNAL"],
        help="Type financial record direction (COST,REVENUE,INTERNAL)",
    )

    p.add_argument(
        "--contract",
        nargs="+",
        help="Filter by contract code(s)",
    )

    p.add_argument(
        "--excel",
        action="store_true",
        help="Export financial records list to Excel",
    )

    p.add_argument("--from", dest="from_date")
    p.add_argument("--to", dest="to_date")


    p.add_argument(
        "--last",
        type=int,
        help="Show last N financial records",
    )

    p.set_defaults(handler=handle_show_financial_records)

REGISTRY.register_group("show", build_show_financial_records)



def handle_show_financial_records(args) -> None:
    services = get_services()
    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return None

    query_service = services.review_query_service

    STATUS_MAP = {
        "NEW": [FinancialRecordStatus.NEW_COST, FinancialRecordStatus.NEW_REVENUE],
        "OPEN": [
            FinancialRecordStatus.NEW_COST,
            FinancialRecordStatus.NEW_REVENUE,
            FinancialRecordStatus.DRAFT,
            FinancialRecordStatus.IN_PROGRESS,
        ],
        "IN_PROGRESS": [FinancialRecordStatus.IN_PROGRESS],
        "PROCESSED": [FinancialRecordStatus.PROCESSED],
        "DELETED": [FinancialRecordStatus.DELETED],
    }

    statuses = (
        list(chain.from_iterable(STATUS_MAP[s] for s in args.status))
        if args.status else None
    )

    buyer_query=FinancialRecordReviewQuery.build_company_query(
        any=args.buyer,
        tax_numbers = args.buyer_nip,
        name = args.buyer_name,
        role = args.buyer_role
    )
    seller_query = FinancialRecordReviewQuery.build_company_query(
        any=args.seller,
        tax_numbers = args.seller_nip,
        name = args.seller_name,
        role = args.seller_role
    )

    review_query = FinancialRecordReviewQuery(
        buyer_query=buyer_query,
        seller_query=seller_query,
        statuses=statuses,
        payment_statuses = [PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID, PaymentStatus.UNKNOWN] if args.unpaid else None,
        from_date=args.from_date,
        to_date=args.to_date,
        contract_codes=args.contract,
        direction=(
            ValueDirection[args.direction]
            if args.direction
            else None
        ),
        organization_id = organization_id,
        actor_user_id=actor_user_id,
        limit = args.last,
    )

    header = FinancialRecordReportHeaderBuilder.from_args(args)

    result_records = services.action_bus.execute(
        action=review_query,
        handler=query_service)
    if not result_records:
        print("No financial records found.")
        return None

    # if args.last:
    #     result_records = result_records[:args.last]

    columns = financial_record_list_columns()
    columns_excel = financial_record_list_columns_excel()

    if args.excel:
        fm = FinancialRecordsShowFileManager(
            organization_id=organization_id,
            prefix="show_records")
        output_path = fm.create_output_file()
        printer: TablePrinter = ExcelPrinter(output_path=output_path)
        printer.print(
            organization_id=str(organization_id),
            items=result_records,
            columns=columns_excel,
            header=header,
        )
        print(f"Financial records list exported to Excel: {output_path}")
        return None

    printer = CmdPrinter()
    printer.print(
        organization_id=str(organization_id),
        items=result_records,
        columns=columns,
        header=header,
    )
    return None




