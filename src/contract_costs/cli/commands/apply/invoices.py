import logging
from pathlib import Path

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY

from contract_costs.services.invoices.excel.invoice_excel_loader import load_invoice_excel_batch
import contract_costs.config as cfg

logger = logging.getLogger(__name__)

def build_apply_invoices(subparsers):
    parser = subparsers.add_parser(
        "invoices",
        help="Apply prepared invoices (Excel import)",
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to invoices excel file",
    )

    parser.set_defaults(handler=handle_apply_invoices)


def handle_apply_invoices(args):

    file = args.file

    services = get_services()

    if file is None:
        path = (
            Path(cfg.INPUTS_INVOICES_NEW_DIR / cfg.INVOICES_EXCEL_FILENAME)
        )
    else:
        path = Path(cfg.INPUTS_INVOICES_NEW_DIR / file)

    excel_path = Path(path)

    batch = load_invoice_excel_batch(excel_path)

    service = services.apply_invoice_excel_batch
    service.apply(batch)

    logger.info(f"Invoices applied from: {excel_path}")


REGISTRY.register_group("apply", build_apply_invoices)
