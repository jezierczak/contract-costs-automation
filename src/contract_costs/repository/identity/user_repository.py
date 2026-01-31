from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.model.identity.user import User


class UserRepository(ABC):

    @abstractmethod
    def add(self, user: User) -> None:
        ...

    @abstractmethod
    def update(self, user: User) -> None:
        ...

    @abstractmethod
    def get(self, user_id: UUID) -> User | None:
        ...

    @abstractmethod
    def get_by_login(self, login: str) -> User | None:
        ...

    @abstractmethod
    def list(self, *, active_only: bool = False) -> list[User]:
        ...

    @abstractmethod
    def exists(self, user_id: UUID) -> bool:
        ...
