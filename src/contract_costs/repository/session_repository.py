from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from contract_costs.model.auth.session import Session


class SessionRepository(ABC):

    @abstractmethod
    def add(self, session: Session) -> None:
        pass

    @abstractmethod
    def get(self, session_id: UUID) -> Session | None:
        pass

    @abstractmethod
    def delete(self, session_id: UUID) -> None:
        pass

    @abstractmethod
    def update(self, session: Session) -> None:
        pass

    @abstractmethod
    def delete_expired(self, now:datetime) -> None:
        pass
