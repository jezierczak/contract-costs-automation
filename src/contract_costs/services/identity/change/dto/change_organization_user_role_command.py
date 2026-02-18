from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command
from contract_costs.model.identity.organization_role import OrganizationRole


@dataclass(frozen=True,slots=True)
@action_type(ActionType.ORG_USER_MANAGEMENT)
class ChangeOrganizationUserRoleCommand(Command):
    target_user_id: UUID
    new_role: OrganizationRole
