from pathlib import Path

from contract_costs.services.invoices.excel.layouts.invoice_excel_layout_resolver import InvoiceExcelView
from contract_costs.services.invoices.review.invoice_review_list_query_service import InvoiceReviewQuery
import contract_costs.config as cfg

INVOICE_EXCEL_INPUT_DIRS = {
    InvoiceExcelView.REVIEW: cfg.INPUTS_INVOICES_REVIEW_DIR,
    InvoiceExcelView.UNPAID: cfg.INPUTS_INVOICES_UNPAID_DIR,
    InvoiceExcelView.FOR_ACCOUNTANT: cfg.INPUTS_INVOICES_ACCOUNTANT_DIR,
}

class InvoiceExcelPathResolver:

    @staticmethod
    def resolve(
        *,
        view: InvoiceExcelView,
        query: InvoiceReviewQuery,
    ) -> Path:
        base_dir = INVOICE_EXCEL_INPUT_DIRS[view]

        base_dir.mkdir(parents=True, exist_ok=True)

        filename = build_invoice_excel_filename(
            view=view,
            query=query,
        )
        return base_dir / filename.lower()

def build_invoice_excel_filename(
    *,
    view: InvoiceExcelView,
    query: InvoiceReviewQuery,
) -> str:
    parts = [f"invoices_{view.value}"]

    if query.from_date or query.to_date:
        parts.append(
            f"{query.from_date or 'start'}_{query.to_date or 'end'}"
        )

    return "_".join(parts) + ".xlsx"

