from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from contract_costs.model.identity.organization_role import OrganizationRole


@dataclass(frozen=True)
class OrganizationUser:
    id: UUID

    organization_id: UUID
    user_id: UUID

    role: OrganizationRole
    is_active: bool

    # audyt
    created_at: datetime
    created_by_user_id: UUID | None

    updated_at: datetime | None = None
    updated_by_user_id: UUID | None = None

    # zaproszenia / onboarding (na przyszłość)
    invited_at: datetime | None = None
    invited_by_user_id: UUID | None = None
    accepted_at: datetime | None = None
