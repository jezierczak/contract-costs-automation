import logging
from pathlib import Path

import contract_costs.config as cfg
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.model.invoice import InvoiceStatus

logger = logging.getLogger(__name__)


# =========================================================
# Builder (argparse)
# =========================================================

def build_prepare_invoices(subparsers):
    """
    prepare invoices [mode]

    Generates Excel with invoices prepared for editing.
    """
    p = subparsers.add_parser(
        "invoices",
        help="Prepare invoices for editing (Excel)",
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

    services.generate_invoice_assignment_excel.execute(
        invoice_status=statuses,
        output_path=output_path,
        # contract_ref=args.contract,
    )

    logger.info("Invoices prepared for editing: %s", output_path)
    print(f"Excel generated: {output_path}")


# =========================================================
# Registry registration
# =========================================================

REGISTRY.register_group("prepare", build_prepare_invoices)
