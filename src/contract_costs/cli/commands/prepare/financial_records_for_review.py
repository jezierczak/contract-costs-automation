import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.show_file_manager import FinancialRecordShowFileManager
from contract_costs.model.financial_record import PaymentStatus, FinancialRecordStatus

from contract_costs.services.financial_records.excel.layouts.financial_record_excel_layout_resolver import FinancialRecordExcelView
from contract_costs.services.financial_records.review.dto.financial_record_review_query import FinancialRecordReviewQuery

logger = logging.getLogger(__name__)

def build_prepare_financial_records_for_review(subparsers):
    p = subparsers.add_parser(
        "for-review",
        aliases=["rev"],
        help="Prepare invoices, for review",
    )

    p.add_argument("--buyer-nip", help="Filter by buyer NIP")
    p.add_argument("--buyer-name", help="Filter by buyer Name")
    p.add_argument("--buyer-role", help="Filter by buyer Role")
    p.add_argument("--buyer", help="Filter by buyer")

    p.add_argument("--seller-nip", help="Filter by seller NIP")
    p.add_argument("--seller-name", help="Filter by seller Name")
    p.add_argument("--seller-role", help="Filter by seller Role")
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

    p.add_argument("--from", dest="from_date")
    p.add_argument("--to", dest="to_date")

    p.add_argument(
        "--only-processed",
        action="store_true",
        help="Include only processed invoices",
    )

    p.set_defaults(handler=handle_prepare_financial_records_for_review)


def handle_prepare_financial_records_for_review(args) -> None:
    services = get_services()
    try:
        organization_id = require_organization_id(services.context)
    except ContextError:
        return

    statuses = [FinancialRecordStatus[s] for s in args.status] if args.status else None

    buyer_query = FinancialRecordReviewQuery.build_company_query(
        any=args.buyer,
        tax_numbers=args.buyer_nip,
        name=args.buyer_name,
        role=args.buyer_role
    )
    seller_query = FinancialRecordReviewQuery.build_company_query(
        any=args.seller,
        tax_numbers=args.seller_nip,
        name=args.seller_name,
        role=args.seller_role
    )

    review_query = FinancialRecordReviewQuery(
        buyer_query=buyer_query,
        seller_query=seller_query,
        statuses=statuses,
        payment_statuses=[PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID,
                          PaymentStatus.UNKNOWN] if args.unpaid else None,
        from_date=args.from_date,
        to_date=args.to_date,
    )

    view = FinancialRecordExcelView.REVIEW
    fm = FinancialRecordShowFileManager(
        organization_id=organization_id,
        view=view
    )
    output_path = fm.create_output_file()
    services.financial_record_excel_export_service.export(
        organization_id=organization_id,
        review_query=review_query,
        view=view,
        output_path=output_path,
    )

    logger.info("Prepared financial records for review: %s", output_path)

