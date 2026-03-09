from contract_costs.model.business_event import BusinessEventLevel
from contract_costs.services.business_event.dto.log_business_event_command import LogBusinessEventCommand


class BusinessEventHelper:

    @staticmethod
    def log(
        *,
        services,
        ctx,
        level: BusinessEventLevel,
        message: str,
        entity_type: str | None = None,
        entity_id = None,
    ) -> None:

        services.action_bus.execute(
            action=LogBusinessEventCommand(
                organization_id=ctx.organization_id,
                actor_user_id=ctx.user_id,
                level=level,
                message=message,
                entity_type=entity_type,
                entity_id=entity_id,
            ),
            handler=services.log_business_event_service,
        )