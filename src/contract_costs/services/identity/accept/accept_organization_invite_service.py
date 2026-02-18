from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.services.identity.accept.dto.accept_organization_invite_command import (
    AcceptOrganizationInviteCommand,
)
from contract_costs.services.identity.exceptions import PermissionDenied
from contract_costs.unit_of_work import UnitOfWork


class AcceptOrganizationInviteService(
    ActionHandler[AcceptOrganizationInviteCommand, None]
):

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._clock = clock

    def execute(
        self,
        *,
        action: AcceptOrganizationInviteCommand,
        uow: UnitOfWork,
    ) -> None:

        membership = uow.organization_users.get_by_org_and_user(
            organization_id=action.organization_id,
            user_id=action.actor_user_id,
        )

        if not membership:
            raise PermissionDenied("User is not a member")

        updated = membership.accept(
            now=self._clock(),
            by_user_id=action.actor_user_id,
        )

        if updated != membership:
            uow.organization_users.update(updated)
