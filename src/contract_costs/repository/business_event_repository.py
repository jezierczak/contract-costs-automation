from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.model.business_event import BusinessEvent


class BusinessEventRepository(ABC):

    @abstractmethod
    def add(self, event: BusinessEvent) -> None: ...

    @abstractmethod
    def list_recent(
        self,
        *,
        organization_id: UUID,
        limit: int = 30,
    ) -> list[BusinessEvent]: ...