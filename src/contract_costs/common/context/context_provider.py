from abc import ABC, abstractmethod
from uuid import UUID


class ContextProvider(ABC):

    @abstractmethod
    def current_user_id(self) -> UUID:
        ...

    @abstractmethod
    def current_organization_id(self) -> UUID:
        ...

    @abstractmethod
    def set_current_organization(self, organization_id: UUID) -> None:
        ...