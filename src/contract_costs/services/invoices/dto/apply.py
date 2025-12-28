from dataclasses import dataclass
from enum import Enum
from uuid import UUID



class InvoiceApplyAction(str, Enum):
    APPLIED = "applied"
    MODIFIED = "modified"
    DELETED = "deleted"
    SKIPPED = "skipped"

@dataclass(frozen=True)
class InvoiceRefResult:
    invoice_id: UUID | None
    action: InvoiceApplyAction
    invoice_number: str
    old_invoice_number: str | None = None