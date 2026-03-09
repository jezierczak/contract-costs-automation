from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.identity.auth.session.dto.logout_command import LogoutCommand
from contract_costs.unit_of_work import UnitOfWork


class LogoutService(
    ActionHandler[LogoutCommand, None]
):
    def execute(self, *, action: LogoutCommand, uow: UnitOfWork) -> None:
        uow.sessions.delete(action.session_id)
