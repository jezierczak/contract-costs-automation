from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.business_event.dto.business_event_list_item_dto import BusinessEventListItemDto
from contract_costs.services.business_event.dto.list_business_events_query_command import ListBusinessEventsQueryCommand


class ListBusinessEventsQueryService(
    ActionHandler[
        ListBusinessEventsQueryCommand,
        list[BusinessEventListItemDto],
    ]
):

    def execute(self, *, action, uow):

        events = uow.business_events.list_recent(
            organization_id=action.organization_id,
            limit=action.limit,
        )

        return [
            BusinessEventListItemDto(
                id=e.id,
                level=e.type,
                message=e.message,
                entity_type=e.entity_type,
                entity_id=e.entity_id,
                created_at=e.created_at,
            )
            for e in events
        ]