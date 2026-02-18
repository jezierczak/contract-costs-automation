import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import FinancialRecordExcelPrepareFileManager
from contract_costs.model.financial_record import PaymentStatus, FinancialRecordStatus
from contract_costs.services.financial_records.excel.dto.financial_record_excel_export_command import \
    FinancialRecordExcelExportCommand

from contract_costs.services.financial_records.excel.layouts.financial_record_excel_layout_resolver import FinancialRecordExcelView
from contract_costs.services.financial_records.review.dto.financial_record_review_query import FinancialRecordReviewQuery

logger = logging.getLogger(__name__)

def build_prepare_financial_records_unpaid(subparsers):
    p = subparsers.add_parser(
        "unpaid",
        aliases=["unp"],
        help="Prepare unpaid financial records, to assign paid",
    )

    p.add_argument("--from", dest="from_date")
    p.add_argument("--to", dest="to_date")

    p.add_argument(
        "--only-processed",
        action="store_true",
        help="Include only processed financial records",
    )

    p.set_defaults(handler=handle_prepare_financial_records_unpaid)




def handle_prepare_financial_records_unpaid(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    review_query = FinancialRecordReviewQuery(
        statuses=[FinancialRecordStatus.PROCESSED, FinancialRecordStatus.SENT_TO_ACCOUNTANT],
        payment_statuses = [PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID, PaymentStatus.UNKNOWN],
        from_date=args.from_date,
        to_date=args.to_date,
        organization_id=organization_id,
        actor_user_id=actor_user_id,
    )

    view = FinancialRecordExcelView.UNPAID
    file_manager = FinancialRecordExcelPrepareFileManager(
        organization_id=organization_id,
        view=view,
        query=review_query,
    )
    output_path = file_manager.prepare_target()

    # services.financial_record_excel_export_service.export(
    #     organization_id=organization_id,
    #     review_query=review_query,
    #     view=view,
    #     output_path=output_path,
    # )
    services.action_bus.execute(
        action=FinancialRecordExcelExportCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            review_query=review_query,
            view=view,
            output_path=output_path,
        ),
        handler=services.financial_record_excel_export_service)

    logger.info("Prepared unpaid financial records for assignment: %s", output_path)
