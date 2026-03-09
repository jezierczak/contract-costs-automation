from datetime import timedelta
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.auth.session import Session
from contract_costs.services.identity.auth.session.dto.create_session_command import CreateSessionCommand
from contract_costs.unit_of_work import UnitOfWork


class CreateSessionService(
    ActionHandler[CreateSessionCommand, UUID]
):
    def __init__(self, clock = utc_now, id_generator=new_uuid):
        self._clock = clock
        self._id_generator = id_generator

    def execute(self, *, action:CreateSessionCommand, uow:UnitOfWork):
        now = self._clock()

        session = Session(
            id=self._id_generator(),
            user_id=action.actor_user_id,
            organization_id=action.organization_id,
            created_at=now,
            expires_at=now + timedelta(hours=12),
        )

        uow.sessions.add(session)

        return session.id
