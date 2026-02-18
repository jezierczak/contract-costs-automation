from dataclasses import dataclass
from pathlib import Path

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command
from contract_costs.services.financial_records.excel.layouts.financial_record_excel_layout_resolver import \
    FinancialRecordExcelView
from contract_costs.services.financial_records.review.dto.financial_record_review_query import \
    FinancialRecordReviewQuery


@dataclass(frozen=True, slots=True)
@action_type(ActionType.FINANCIAL_RECORD_MANAGEMENT)
class FinancialRecordExcelExportCommand(Command):
    review_query: FinancialRecordReviewQuery
    view: FinancialRecordExcelView
    output_path: Path