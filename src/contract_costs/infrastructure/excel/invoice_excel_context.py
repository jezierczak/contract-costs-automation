from dataclasses import dataclass
from enum import Enum

from contract_costs.infrastructure.excel.checkbox_options import CheckBoxOptions


class FinancialRecordExcelContext(Enum):
    UNPAID = "unpaid"
    ACCOUNTANT = "accountant"

@dataclass(frozen=True)
class FinancialRecordExcelSpec:
    action_column: int
    record_id_column: int
    allowed_actions: set[str]

EXCEL_SPECS = {
    FinancialRecordExcelContext.UNPAID: FinancialRecordExcelSpec(
        action_column=0,
        record_id_column=1,
        allowed_actions={CheckBoxOptions.YES.value.lower()},
    ),
    FinancialRecordExcelContext.ACCOUNTANT: FinancialRecordExcelSpec(
        action_column=0,
        record_id_column=1,
        allowed_actions={"approved","reopen"},
    ),
}
