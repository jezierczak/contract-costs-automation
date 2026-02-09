from contract_costs.action_bus.ROLE_PERMISSIONS import ROLE_PERMISSIONS
from contract_costs.action_bus.action import Action
from contract_costs.action_bus.permission_resolver import PermissionResolver


class PermissionValidator:

    def __init__(self, permission_resolver: PermissionResolver):
        self._permission_resolver = permission_resolver

    def validate(self, action: Action) -> None:

        action_type = action.action_type #getattr(type(action), "__action_type__", None)

        if action_type is None:
            raise RuntimeError(
                f"{type(action).__name__} missing @action_type decorator"
            )

        allowed = self._permission_resolver.has_permission(
            organization_id=action.organization_id,
            user_id=action.actor_user_id,
            action_type=action_type,
        )

        if not allowed:
            raise PermissionError("Not allowed")


        # Query → tylko membership check
        # if isinstance(action, Query):
        #     return
        #
        # # Command → wymagany dekorator
        # if not isinstance(action, Command):
        #     raise RuntimeError(
        #         f"Unsupported action type: {type(action).__name__}"
        #     )

        # allowed_roles = getattr(type(action), "__allowed_roles__", None)
        #
        # if allowed_roles is None:
        #     raise RuntimeError(
        #         f"{type(action).__name__} missing @requires_roles decorator"
        #     )
        #
        # if membership.role not in allowed_roles:
        #     raise PermissionError("Not allowed")

