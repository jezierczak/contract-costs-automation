from datetime import datetime
from uuid import UUID
from typing import Dict

from contract_costs.model.auth.session import Session
from contract_costs.repository.session_repository import SessionRepository


class InMemorySessionRepository(SessionRepository):

    def __init__(self):
        self._storage: Dict[UUID, Session] = {}

    def add(self, session: Session) -> None:
        self._storage[session.id] = session

    def get(self, session_id: UUID) -> Session | None:
        return self._storage.get(session_id)

    def delete(self, session_id: UUID) -> None:
        self._storage.pop(session_id, None)

    def update(self, session: Session) -> None:
        if session.id in self._storage:
            self._storage[session.id] = session

    def delete_expired(self, now:datetime) -> None:
        self._storage = {
            k: v for k, v in self._storage.items()
            if v.expires_at >= now
        }
