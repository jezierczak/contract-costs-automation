from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class CostTypeExport:
    id: UUID
    code: str
    name: str
