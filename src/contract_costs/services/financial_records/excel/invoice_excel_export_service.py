from pathlib import Path
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.infrastructure.excel.base_excel_exporter import BaseExcelExporter
from contract_costs.services.financial_records.excel.dto.financial_record_excel_export_command import \
    FinancialRecordExcelExportCommand
from contract_costs.services.financial_records.excel.layouts.financial_record_excel_layout_resolver import FinancialRecordExcelView, \
    FinancialRecordExcelLayoutResolver
from contract_costs.services.financial_records.review.financial_record_review_list_query_service import FinancialRecordReviewListQueryService, \
    FinancialRecordReviewQuery
from contract_costs.unit_of_work import UnitOfWork


class FinancialRecordExcelExportService(
    ActionHandler[FinancialRecordExcelExportCommand, None]
):

    def __init__(
        self,
        review_query_service: FinancialRecordReviewListQueryService,
        exporter: BaseExcelExporter,
    ):
        self._query = review_query_service
        self._exporter = exporter

    def execute(
        self,
        *,
        action: FinancialRecordExcelExportCommand,
        uow: UnitOfWork,
    ) -> None:

        items = self._query.execute(
            action=action.review_query,
            uow=uow,
        )

        columns = FinancialRecordExcelLayoutResolver.resolve(action.view)

        self._exporter.export(
            items=items,
            columns=columns,
            output_path=action.output_path,
            sheet_name=action.view.value,
            organization_id=action.organization_id,
        )