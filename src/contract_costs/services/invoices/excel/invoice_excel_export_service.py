from pathlib import Path

from contract_costs.infrastructure.excel.base_excel_exporter import BaseExcelExporter
from contract_costs.services.invoices.excel.layouts.invoice_excel_layout_resolver import InvoiceExcelView, \
    InvoiceExcelLayoutResolver
from contract_costs.services.invoices.review.invoice_review_list_query_service import InvoiceReviewListQueryService, \
    InvoiceReviewQuery


class InvoiceExcelExportService:

    def __init__(
        self,
        review_query_service: InvoiceReviewListQueryService,
        exporter: BaseExcelExporter,
    ):
        self._query = review_query_service
        self._exporter = exporter

    def export(
        self,
        *,
        review_query: InvoiceReviewQuery,
        view: InvoiceExcelView,
        output_path: Path,
    ) -> None:
        items = self._query.list_for_review(review_query)
        columns = InvoiceExcelLayoutResolver.resolve(view)

        self._exporter.export(
            items=items,
            columns=columns,
            output_path=output_path,
            sheet_name=view.value,
        )
