import logging

from contract_costs.cli.context import get_services
from contract_costs.infrastructure.excel.invoice_excel_context import InvoiceExcelContext
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InvoiceExcelPrepareFileManager
from contract_costs.services.invoices.excel.layouts.invoice_excel_layout_resolver import InvoiceExcelView
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery

logger = logging.getLogger(__name__)

def build_apply_invoices_to_accountant(subparsers):
    parser = subparsers.add_parser(
        "to-accountant",
        aliases=["acc"],
        help="Set invoices sent to accountant",
    )
    #
    # parser.add_argument(
    #     "file",
    #     nargs="?",
    #     help="Path to invoices excel file",
    # )

    parser.set_defaults(handler=handle_apply_invoices_to_accountant)

def handle_apply_invoices_to_accountant(args):
    services = get_services()
    # if args.file:
    #     path = Path(args.file)
    # else:
        # 🔑 TA SAMA LOGIKA CO W PREPARE
    file_manager = InvoiceExcelPrepareFileManager(
        view=InvoiceExcelView.FOR_ACCOUNTANT,
        query=InvoiceReviewQuery(only_ready_for_accountant=True)
    )
    path= file_manager.get_active_file()
    #     path = InvoiceExcelPathResolver.resolve(
    #         view=InvoiceExcelView.FOR_ACCOUNTANT,
    #         query=InvoiceReviewQuery(
    #             only_ready_for_accountant=True
    #         ),
    #     )
    #
    # if not path.exists():
    #     raise RuntimeError(f"Excel file not found: {path}")
    commands = services.invoice_action_excel_loader.load(path,context=InvoiceExcelContext.ACCOUNTANT)

    for cmd in commands:
        services.invoice_action_service.execute(cmd)


    file_manager.mark_processed()
    logger.info(
        "Invoices sent to accountant: %d",
        len(commands),
    )

    print(f"✔ Sent to accountant: {len(commands)} invoices")
