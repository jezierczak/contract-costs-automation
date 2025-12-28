import logging

import contract_costs.config as cfg
from contract_costs.cli.context import get_services
from contract_costs.model.invoice import InvoiceStatus

logger = logging.getLogger(__name__)


def handle_showexcel_invoices(mode: str) -> None:
    services = get_services()

    statuses = {
        "new": [InvoiceStatus.NEW],
        "in_progress": [InvoiceStatus.IN_PROGRESS],
        "open": [InvoiceStatus.NEW, InvoiceStatus.IN_PROGRESS],
    }[mode if mode else "open"]

    # if mode == "new":
    output_path = (
            cfg.INPUTS_INVOICES_NEW_DIR / cfg.INVOICES_EXCEL_FILENAME
        )
    # else:
    #     output_path = (
    #             cfg.INPUTS_INVOICES_ASSIGN_DIR / cfg.INVOICES_EXCEL_FILENAME
    #     )

    services.generate_invoice_assignment_excel.execute(
        invoice_status=statuses,
        output_path=output_path
    )

    logger.info(f"Excel generated: {output_path}")
