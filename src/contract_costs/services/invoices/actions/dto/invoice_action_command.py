from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator


class InvoiceAction(str, Enum):
    MARK_PAID = "mark_paid"
    MARK_UNPAID = "mark_unpaid"
    MARK_SENT_TO_ACCOUNTANT = "mark_sent_to_accountant"
    REOPEN = "reopen"



class InvoiceSelector(BaseModel):
    invoice_id: UUID | None = None
    invoice_number: str | None = None

    @model_validator(mode="after")
    def exactly_one(self):
        if bool(self.invoice_id) == bool(self.invoice_number):
            raise ValueError(
                "Provide exactly one of invoice_id or invoice_number"
            )
        return self

    # @model_validator(mode="after")
    # def at_least_one_selector(self):
    #     if not self.selectors:
    #         raise ValueError("At least one invoice selector is required")
    #     return self


class InvoiceActionCommand(BaseModel):
    action: InvoiceAction
    selectors: list[InvoiceSelector]
    payload: dict[str, Any] | None = None
