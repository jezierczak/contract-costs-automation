from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from contract_costs.model.company import CompanyType


class InvoiceSource(Enum):
    PDF_IMAGE = "pdf_image"
    EXCEL = "excel"

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
    buyer_role: CompanyType
    seller_role: CompanyType
    old_invoice_number: str | None = None
