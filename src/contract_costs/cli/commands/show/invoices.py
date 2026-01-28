import logging

from contract_costs.cli.commands.header_builder.invoice_report_header_builder import InvoiceReportHeaderBuilder
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.printers.table_printer.table_printer import TablePrinter
from contract_costs.cli.printers.table_printer.excel_printer import ExcelPrinter
from contract_costs.infrastructure.filesystem.show_file_manager import  InvoicesShowFileManager

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.model.invoice import InvoiceStatus, PaymentStatus
from contract_costs.model.value_direction import ValueDirection
from contract_costs.reports.invoices.invoice_list_columns import invoice_list_columns
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery

logger = logging.getLogger(__name__)


def build_show_invoices(subparsers):
    p = subparsers.add_parser(
        "invoices",
        help="Show invoices",
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
        help="Filter by invoice status",
    )
    p.add_argument(
        "--unpaid",
        action="store_true",
        help="Show only unpaid invoices",
    )

    p.add_argument(
        "--direction",
        choices=["COST", "REVENUE", "INTERNAL"],
        help="Type invoice direction (COST,REVENUE,INTERNAL)",
    )

    p.add_argument(
        "--contract",
        nargs="+",
        help="Filter by contract code(s)",
    )

    p.add_argument(
        "--excel",
        action="store_true",
        help="Export invoices list to Excel",
    )

    p.add_argument("--from", dest="from_date")
    p.add_argument("--to", dest="to_date")


    p.add_argument(
        "--last",
        type=int,
        help="Show last N invoices",
    )

    p.set_defaults(handler=handle_show_invoices)

REGISTRY.register_group("show", build_show_invoices)



def handle_show_invoices(args) -> None:
    services = get_services()
    query_service = services.review_query_service

    statuses = [InvoiceStatus[s] for s in args.status] if args.status else None

    buyer_query=InvoiceReviewQuery.build_company_query(
        any=args.buyer,
        tax_numbers = args.buyer_nip,
        name = args.buyer_name,
        role = args.buyer_role
    )
    seller_query = InvoiceReviewQuery.build_company_query(
        any=args.seller,
        tax_numbers = args.seller_nip,
        name = args.seller_name,
        role = args.seller_role
    )

    review_query = InvoiceReviewQuery(
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
        )
    )

    header = InvoiceReportHeaderBuilder.from_args(args)

    result_invoices = query_service.list_for_review(review_query)
    if not result_invoices:
        print("No invoices found.")
        return

    if args.last:
        result_invoices = result_invoices[:args.last]

    columns = invoice_list_columns()

    if args.excel:
        fm = InvoicesShowFileManager(prefix="show_invoices")
        output_path = fm.create_output_file()
        printer: TablePrinter = ExcelPrinter(output_path=output_path)
        printer.print(
            items=result_invoices,
            columns=columns,
            header=header,
        )
        print(f"Invoice list exported to Excel: {output_path}")
        return

    printer = CmdPrinter()
    printer.print(
        items=result_invoices,
        columns=columns,
        header=header,
    )




