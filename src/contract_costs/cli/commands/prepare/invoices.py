import logging
from pathlib import Path

import contract_costs.config as cfg
from contract_costs.cli.commands.prepare.invoices_for_accountant import build_prepare_invoices_for_accountant
from contract_costs.cli.commands.prepare.invoices_for_review import build_prepare_invoices_for_review
from contract_costs.cli.commands.prepare.invoices_unpaid import build_prepare_invoices_unpaid
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.model.invoice import InvoiceStatus

logger = logging.getLogger(__name__)


# =========================================================
# Builder (argparse)
# =========================================================


def build_prepare_invoices(subparsers):
    p = subparsers.add_parser(
        "invoices",
        help="Prepare invoices workflows",
    )

    invoice_sub = p.add_subparsers(
        dest="workflow",
        required=True,
    )

    build_prepare_invoices_for_assignment(invoice_sub)
    build_prepare_invoices_for_accountant(invoice_sub)
    build_prepare_invoices_unpaid(invoice_sub)
    build_prepare_invoices_for_review(invoice_sub)

def build_prepare_invoices_for_assignment(subparsers):
    """
    prepare invoices

    Generates Excel with invoices prepared for editing.
    """
    p = subparsers.add_parser(
        "for-assignment",
        help="Prepare invoices for assignment/editing",
    )

    p.add_argument(
        "mode",
        nargs="?",
        choices=["new", "in_progress", "open"],
        default="open",
        help="Invoice status filter (default: open)",
    )

    p.add_argument(
        "--contract",
        help="Filter by contract code or UUID (optional)",
    )

    p.add_argument(
        "--excel",
        action="store_true",
        help="Generate Excel output (default behavior)",
    )

    p.set_defaults(handler=handle_prepare_invoices)


# =========================================================
# Handler
# =========================================================

def handle_prepare_invoices(args) -> None:
    services = get_services()

    statuses = {
        "new": [InvoiceStatus.NEW],
        "in_progress": [InvoiceStatus.IN_PROGRESS],
        "open": [InvoiceStatus.NEW, InvoiceStatus.IN_PROGRESS],
    }[args.mode if args.mode else "open"]

    output_path: Path = (
        cfg.INPUTS_INVOICES_NEW_DIR / cfg.INVOICES_EXCEL_FILENAME
    )

    bundle = services.generate_invoice_assignment_bundle.execute(
        invoice_status=statuses,
        # contract_ref=args.contract,
    )
    services.export_invoice_assignment_excel_service.execute(
        bundle=bundle,
        output_path=output_path )

    logger.info("Invoices prepared for editing: %s", output_path)
    logger.info(f"Excel generated: {output_path}")


# =========================================================
# Registry registration
# =========================================================

REGISTRY.register_group("prepare", build_prepare_invoices)
