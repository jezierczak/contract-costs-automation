from pathlib import Path
from uuid import UUID

from contract_costs.infrastructure.excel.base_excel_exporter import BaseExcelExporter
from contract_costs.services.financial_records.excel.layouts.financial_record_excel_layout_resolver import FinancialRecordExcelView, \
    FinancialRecordExcelLayoutResolver
from contract_costs.services.financial_records.review.financial_record_review_list_query_service import FinancialRecordReviewListQueryService, \
    FinancialRecordReviewQuery


class FinancialRecordExcelExportService:

    def __init__(
        self,
        review_query_service: FinancialRecordReviewListQueryService,
        exporter: BaseExcelExporter,
    ):
        self._query = review_query_service
        self._exporter = exporter

    def export(
        self,
        *,
        organization_id: UUID,
        review_query: FinancialRecordReviewQuery,
        view: FinancialRecordExcelView,
        output_path: Path,
    ) -> None:
        items = self._query.list_for_review(
            organization_id=organization_id,
            review_query=review_query)
        columns = FinancialRecordExcelLayoutResolver.resolve(view)

        self._exporter.export(
            items=items,
            columns=columns,
            output_path=output_path,
            sheet_name=view.value,
            organization_id=organization_id
        )
