from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator

from contract_costs.infrastructure.excel.invoice_excel_context import FinancialRecordExcelContext


class FinancialRecordAction(Enum):
    MARK_PAID = "mark_paid"
    MARK_UNPAID = "mark_unpaid"
    MARK_SENT_TO_ACCOUNTANT = "mark_sent_to_accountant"
    REOPEN = "reopen"

def financial_record_action_from_excel(
        *,
        context: FinancialRecordExcelContext,
        raw: str,
) -> FinancialRecordAction:
    if not raw:
        raise ValueError("Empty excel action")

    key = f"{raw.strip().lower()}-{context.value.lower()}"


    mapping: dict[str, FinancialRecordAction] = {
        "approved-accountant": FinancialRecordAction.MARK_SENT_TO_ACCOUNTANT,
        "yes-unpaid": FinancialRecordAction.MARK_PAID,
        "reopen-accountant": FinancialRecordAction.REOPEN,
    }

    try:
        return mapping[key]
    except KeyError:
        raise ValueError(
            f"Unknown excel action '{raw}' for context '{context.value}'"
        )


class FinancialRecordSelector(BaseModel):
    record_id: UUID | None = None
    record_reference: str | None = None

    @model_validator(mode="after")
    def exactly_one(self):
        if bool(self.record_id) == bool(self.record_reference):
            raise ValueError(
                "Provide exactly one of invoice_id or invoice_number"
            )
        return self

    # @model_validator(mode="after")
    # def at_least_one_selector(self):
    #     if not self.selectors:
    #         raise ValueError("At least one invoice selector is required")
    #     return self


class FinancialRecordActionCommand(BaseModel):
    action: FinancialRecordAction
    selectors: list[FinancialRecordSelector]
    payload: dict[str, Any] | None = None
