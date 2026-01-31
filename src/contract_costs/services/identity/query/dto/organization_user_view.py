from datetime import datetime
from dataclasses import dataclass
from uuid import UUID

from contract_costs.model.identity.organization_role import OrganizationRole


@dataclass(frozen=True)
class OrganizationUserView:
    user_id: UUID
    login: str
    full_name: str | None
    email: str | None

    role: OrganizationRole
    is_active: bool

    invited_at: datetime | None
    accepted_at: datetime | None
