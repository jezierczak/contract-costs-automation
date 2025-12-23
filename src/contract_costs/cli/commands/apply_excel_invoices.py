from pathlib import Path

import contract_costs.config as cfg

from contract_costs.cli.context import get_services
from contract_costs.services.invoices.excel.invoice_excel_loader import (
    load_invoice_excel_batch,
)


def handle_applyexcel_invoices(file: str | None) -> None:
    services = get_services()

    if file is None:
        file = (
            cfg.INPUTS_INVOICES_NEW_DIR / cfg.INVOICES_EXCEL_FILENAME
            )

    excel_path = Path(file)

    batch = load_invoice_excel_batch(excel_path)

    service = services.apply_invoice_excel_batch
    service.apply(batch)

    print(f"Invoices applied from: {excel_path}")
