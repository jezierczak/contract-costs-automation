from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ActivateCompanyCommand:
    organization_id: UUID
    company_id: UUID
    actor_user_id: UUID
