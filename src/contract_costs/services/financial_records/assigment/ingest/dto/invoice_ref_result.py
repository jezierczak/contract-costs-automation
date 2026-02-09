from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from contract_costs.model.company import CompanyType


class InvoiceSource(Enum):
    PDF_IMAGE = "pdf_image"
    EXCEL = "excel"

class RecordApplyAction(str, Enum):
    APPLIED = "applied"
    MODIFIED = "modified"
    DELETED = "deleted"
    SKIPPED = "skipped"

@dataclass(frozen=True)
class FinancialRecordRefResult:
    record_id: UUID | None
    action: RecordApplyAction
    record_reference: str
    buyer_role: CompanyType
    seller_role: CompanyType
    old_record_reference: str | None = None
