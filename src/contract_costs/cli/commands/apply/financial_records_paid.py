import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.excel.invoice_excel_context import FinancialRecordExcelContext
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import FinancialRecordExcelPrepareFileManager
from contract_costs.model.financial_record import FinancialRecordStatus, PaymentStatus
from contract_costs.services.financial_records.excel.layouts.financial_record_excel_layout_resolver import FinancialRecordExcelView
from contract_costs.services.financial_records.review.dto.financial_record_review_query import FinancialRecordReviewQuery

logger = logging.getLogger(__name__)

def build_apply_financial_records_paid(subparsers):
    parser = subparsers.add_parser(
        "paid",
        aliases=["unp"],
        help="Apply financial records paid",
    )

    parser.set_defaults(handler=handle_apply_financial_records_paid)

def handle_apply_financial_records_paid(args):
    services = get_services()
    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return
    # 🔑 TA SAMA LOGIKA CO W PREPARE
    file_manager = FinancialRecordExcelPrepareFileManager(
        organization_id=organization_id,
        view=FinancialRecordExcelView.UNPAID,
        query=FinancialRecordReviewQuery(
            statuses=[FinancialRecordStatus.PROCESSED, FinancialRecordStatus.SENT_TO_ACCOUNTANT],
            payment_statuses=[PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID, PaymentStatus.UNKNOWN],
        ),
    )
    path = file_manager.get_active_file()

    commands = services.financial_record_action_excel_loader.load(path, context=FinancialRecordExcelContext.UNPAID)


    for cmd in commands:
        services.financial_record_action_service.execute(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            cmd=cmd,
        )

    file_manager.mark_processed()
    logger.info(
        "Records set paid: %d",
        len(commands),
    )

    print(f"✔ Set paid: {len(commands)} invoices")
