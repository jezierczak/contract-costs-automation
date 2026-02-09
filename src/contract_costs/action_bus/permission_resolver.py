from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.action_bus.ROLE_PERMISSIONS import ROLE_PERMISSIONS
from contract_costs.action_bus.action_type import ActionType
from contract_costs.model.identity.organization_role import OrganizationRole


class PermissionResolver(ABC):

    @abstractmethod
    def has_permission(
        self,
        *,
        organization_id: UUID,
        user_id: UUID,
        action_type: ActionType
    ) -> bool:
        ...


class MySqlPermissionResolver(PermissionResolver):

    def __init__(self, org_user_repo):
        self._org_user_repo = org_user_repo

    def has_permission(
        self,
        *,
        organization_id: UUID,
        user_id: UUID,
        action_type: ActionType,
    ) -> bool:

        membership = self._org_user_repo.get_by_org_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )

        if not membership or not membership.is_active:
            return False

        if membership.role == OrganizationRole.OWNER:
            return True

        allowed_roles = ROLE_PERMISSIONS.get(action_type)

        if not allowed_roles:
            return False

        return membership.role in allowed_roles
