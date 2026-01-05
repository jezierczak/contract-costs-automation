from enum import Enum

from contract_costs.services.invoices.excel.layouts.for_accountant_layout import ACCOUNTANT_COLUMNS
from contract_costs.services.invoices.excel.layouts.review_layout import REVIEW_COLUMNS
from contract_costs.services.invoices.excel.layouts.unpaid_layout import UNPAID_COLUMNS


class InvoiceExcelView(Enum):
    REVIEW = "Review"
    FOR_ACCOUNTANT = "For_Accountant"
    UNPAID = "Unpaid"


class InvoiceExcelLayoutResolver:

    @staticmethod
    def resolve(view: InvoiceExcelView):
        match view:
            case InvoiceExcelView.REVIEW:
                return REVIEW_COLUMNS
            case InvoiceExcelView.FOR_ACCOUNTANT:
                return ACCOUNTANT_COLUMNS
            case InvoiceExcelView.UNPAID:
                return UNPAID_COLUMNS
            case _:
                raise ValueError(f"Unsupported excel view: {view}")
