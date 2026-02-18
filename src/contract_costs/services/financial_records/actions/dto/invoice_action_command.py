from dataclasses import dataclass
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command
from contract_costs.infrastructure.excel.invoice_excel_context import FinancialRecordExcelContext
from contract_costs.model.company import Company


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


@dataclass(frozen=True,slots=True)
@action_type(ActionType.FINANCIAL_RECORD_APPROVAL)
class FinancialRecordActionCommand(Command):
    action: FinancialRecordAction
    selectors: list[FinancialRecordSelector]
    payload: dict[str, Any] | None = None
