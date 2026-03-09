from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.business_event.business_event_service import BusinessEventService
from contract_costs.services.business_event.dto.log_business_event_command import LogBusinessEventCommand
from contract_costs.unit_of_work import UnitOfWork


class LogBusinessEventService(
    ActionHandler[LogBusinessEventCommand, None]
):

    def __init__(self, events_log: BusinessEventService):
        self._events = events_log

    def execute(self, *, action: LogBusinessEventCommand, uow: UnitOfWork) -> None:

        self._events.log(
            organization_id=action.organization_id,
            actor_user_id=action.actor_user_id,
            level=action.level,
            message=action.message,
            entity_type=action.entity_type,
            entity_id=action.entity_id,
            uow=uow,
        )

        # uow.business_events.add(
        #     BusinessEvent(
        #         id=self._id(),
        #         organization_id=action.organization_id,
        #         type=action.level,
        #         message=action.message,
        #         entity_type=action.entity_type,
        #         entity_id=action.entity_id,
        #         created_at=self._clock(),
        #         created_by_user_id=action.actor_user_id,
        #     )
        #)