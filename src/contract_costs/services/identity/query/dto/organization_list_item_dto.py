from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class OrganizationListItemDTO:
    id: UUID
    code: str
    name: str
    is_active: bool
    role: str | None  # OWNER / ADMIN / USER (jeśli kontekst usera)
