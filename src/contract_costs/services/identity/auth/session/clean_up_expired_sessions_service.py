from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.services.identity.auth.session.dto.clean_up_expired_sessions_command import \
    CleanupExpiredSessionsCommand


class CleanupExpiredSessionsService(
    ActionHandler[CleanupExpiredSessionsCommand, None]
):

    def execute(self, *, action, uow):

        session_repo = uow.sessions

        session_repo.delete_expired(utc_now())
