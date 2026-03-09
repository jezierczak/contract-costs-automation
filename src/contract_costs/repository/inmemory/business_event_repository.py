from uuid import UUID

from contract_costs.model.business_event import BusinessEvent
from contract_costs.repository.business_event_repository import BusinessEventRepository


class InMemoryBusinessEventRepository(BusinessEventRepository):

    def __init__(self):
        self._events: dict[UUID, BusinessEvent] = {}

    def add(self, event):
        self._events[event.id] = event

    def list_recent(self, *, organization_id, limit=30):
        events = [
            e for e in self._events.values()
            if e.organization_id == organization_id
        ]
        return sorted(
            events,
            key=lambda e: e.created_at,
            reverse=True,
        )[:limit]