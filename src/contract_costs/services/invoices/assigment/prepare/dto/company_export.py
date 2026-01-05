from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class CompanyExport:
    id: UUID
    name: str
    tax_number: str
