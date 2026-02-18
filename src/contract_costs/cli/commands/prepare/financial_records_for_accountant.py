import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import FinancialRecordExcelPrepareFileManager
from contract_costs.services.financial_records.excel.dto.financial_record_excel_export_command import \
    FinancialRecordExcelExportCommand
from contract_costs.services.financial_records.excel.layouts.financial_record_excel_layout_resolver import FinancialRecordExcelView
from contract_costs.services.financial_records.review.financial_record_review_list_query_service import FinancialRecordReviewQuery

logger = logging.getLogger(__name__)

def build_prepare_financial_records_for_accountant(subparsers):
    p = subparsers.add_parser(
        "for-accountant",
        aliases=["acc"],
        help="Prepare financial records for sending to accountant",
    )

    p.add_argument("--from", dest="from_date")
    p.add_argument("--to", dest="to_date")

    p.add_argument(
        "--include-unprocessed",
        dest="include_unprocessed",
        action="store_true",
        help="Include financial records not yet processed",
    )

    p.set_defaults(handler=handle_prepare_financial_records_for_accountant)


def handle_prepare_financial_records_for_accountant(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    review_query = FinancialRecordReviewQuery(
        from_date=args.from_date,
        to_date=args.to_date,
        only_ready_for_accountant=not args.include_unprocessed,
        organization_id=organization_id,
        actor_user_id=actor_user_id
    )

    view = FinancialRecordExcelView.FOR_ACCOUNTANT

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

    logger.info("Prepared financial records for accountant: %s", output_path)

