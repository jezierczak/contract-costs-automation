from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class UseOrganizationCommand:
    user_id: UUID
    organization_code: str
