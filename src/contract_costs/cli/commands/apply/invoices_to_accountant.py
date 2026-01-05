import logging
from pathlib import Path

from contract_costs.cli.context import get_services
from contract_costs.services.invoices.excel.invoice_excel_path_resolver import InvoiceExcelPathResolver
from contract_costs.services.invoices.excel.layouts.invoice_excel_layout_resolver import InvoiceExcelView
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery

logger = logging.getLogger(__name__)

def build_apply_invoices_to_accountant(subparsers):
    parser = subparsers.add_parser(
        "to-accountant",
        help="Set invoices sent to accountant",
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to invoices excel file",
    )

    parser.set_defaults(handler=handle_apply_invoices_to_accountant)

def handle_apply_invoices_to_accountant(args):
    services = get_services()
    if args.file:
        path = Path(args.file)
    else:
        # 🔑 TA SAMA LOGIKA CO W PREPARE
        path = InvoiceExcelPathResolver.resolve(
            view=InvoiceExcelView.FOR_ACCOUNTANT,
            query=InvoiceReviewQuery(
                only_ready_for_accountant=True
            ),
        )

    if not path.exists():
        raise RuntimeError(f"Excel file not found: {path}")
    cmd = services.invoice_action_excel_loader.load_to_accountant(path)

    services.invoice_action_service.execute(cmd)

    logger.info(
        "Invoices sent to accountant: %d",
        len(cmd.selectors),
    )

    print(f"✔ Sent to accountant: {len(cmd.selectors)} invoices")
