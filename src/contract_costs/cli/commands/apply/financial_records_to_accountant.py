import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_user_id, require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.excel.invoice_excel_context import FinancialRecordExcelContext
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import FinancialRecordExcelPrepareFileManager
from contract_costs.services.financial_records.excel.layouts.financial_record_excel_layout_resolver import FinancialRecordExcelView
from contract_costs.services.financial_records.review.dto.financial_record_review_query import FinancialRecordReviewQuery

logger = logging.getLogger(__name__)

def build_apply_financial_records_to_accountant(subparsers):
    parser = subparsers.add_parser(
        "to-accountant",
        aliases=["acc"],
        help="Set financial records sent to accountant",
    )

    parser.set_defaults(handler=handle_apply_financial_records_to_accountant)

def handle_apply_financial_records_to_accountant(args):
    services = get_services()
    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    # 🔑 TA SAMA LOGIKA CO W PREPARE
    file_manager = FinancialRecordExcelPrepareFileManager(
        organization_id=organization_id,
        view=FinancialRecordExcelView.FOR_ACCOUNTANT,
        query=FinancialRecordReviewQuery(only_ready_for_accountant=True)
    )
    path= file_manager.get_active_file()

    commands = services.financial_record_action_excel_loader.load(path, context=FinancialRecordExcelContext.ACCOUNTANT)

    for cmd in commands:
        services.financial_record_action_service.execute(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            cmd=cmd
        )


    file_manager.mark_processed()
    logger.info(
        "Financial records sent to accountant: %d (org=%s)",
        len(commands),
        organization_id
    )

    print(f"✔ Sent to accountant: {len(commands)} financial records")
