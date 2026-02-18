from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class ValueTypeExport:
    id: UUID
    code: str
    name: str
