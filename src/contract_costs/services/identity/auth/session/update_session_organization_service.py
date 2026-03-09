from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.identity.auth.session.dto.update_session_organization_command import (
    UpdateSessionOrganizationCommand,
)
from contract_costs.services.identity.exceptions import PermissionDenied
from contract_costs.unit_of_work import UnitOfWork


class UpdateSessionOrganizationService(
    ActionHandler[UpdateSessionOrganizationCommand, None]
):

    def execute(self, *, action: UpdateSessionOrganizationCommand, uow:UnitOfWork):

        session_repo = uow.sessions

        session = session_repo.get(action.session_id)

        if not session:
            raise PermissionDenied("Session not found")

        updated = session.with_organization(
            organization_id=action.organization_id
        )

        session_repo.update(updated)
