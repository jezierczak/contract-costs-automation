from enum import Enum

from contract_costs.services.financial_records.excel.layouts.for_accountant_layout import ACCOUNTANT_COLUMNS
from contract_costs.services.financial_records.excel.layouts.review_layout import REVIEW_COLUMNS
from contract_costs.services.financial_records.excel.layouts.unpaid_layout import UNPAID_COLUMNS


class FinancialRecordExcelView(Enum):
    REVIEW = "Review"
    FOR_ACCOUNTANT = "Accountant"
    UNPAID = "Unpaid"


class FinancialRecordExcelLayoutResolver:

    @staticmethod
    def resolve(view: FinancialRecordExcelView):
        match view:
            case FinancialRecordExcelView.REVIEW:
                return REVIEW_COLUMNS
            case FinancialRecordExcelView.FOR_ACCOUNTANT:
                return ACCOUNTANT_COLUMNS
            case FinancialRecordExcelView.UNPAID:
                return UNPAID_COLUMNS
            case _:
                raise ValueError(f"Unsupported excel view: {view}")
