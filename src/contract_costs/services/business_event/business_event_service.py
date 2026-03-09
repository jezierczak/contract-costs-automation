from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.business_event import BusinessEvent


class BusinessEventService:

    def __init__(self, clock=utc_now, id_generator=new_uuid):
        self._clock = clock
        self._id = id_generator

    def log(
        self,
        *,
        organization_id,
        actor_user_id,
        level,
        message,
        entity_type,
        entity_id,
        uow,
    ):
        uow.business_events.add(
            BusinessEvent(
                id=self._id(),
                organization_id=organization_id,
                type=level,
                message=message,
                entity_type=entity_type,
                entity_id=entity_id,
                created_at=self._clock(),
                created_by_user_id=actor_user_id,
            )
        )