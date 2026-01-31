from dataclasses import dataclass
from uuid import UUID

from contract_costs.model.identity.organization_role import OrganizationRole


@dataclass(frozen=True)
class ChangeOrganizationUserRoleCommand:
    organization_id: UUID
    target_user_id: UUID
    new_role: OrganizationRole
    actor_user_id: UUID
