from dataclasses import dataclass
from enum import Enum

from contract_costs.infrastructure.excel.checkbox_options import CheckBoxOptions


class InvoiceExcelContext(Enum):
    UNPAID = "unpaid"
    ACCOUNTANT = "accountant"

@dataclass(frozen=True)
class InvoiceExcelSpec:
    action_column: int
    invoice_id_column: int
    allowed_actions: set[str]

EXCEL_SPECS = {
    InvoiceExcelContext.UNPAID: InvoiceExcelSpec(
        action_column=0,
        invoice_id_column=1,
        allowed_actions={CheckBoxOptions.YES.value.lower()},
    ),
    InvoiceExcelContext.ACCOUNTANT: InvoiceExcelSpec(
        action_column=0,
        invoice_id_column=1,
        allowed_actions={"approved","reopen"},
    ),
}
