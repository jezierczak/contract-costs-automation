from abc import ABC, abstractmethod
from uuid import UUID
from contract_costs.model.cost_type import (CostType)

class CostTypeRepository(ABC):
    @abstractmethod
    def add(self, cost_type: CostType) -> None:
        (...
    @abstractmethod)
    def get(self, cost_type_id: UUID) -> CostType | None:
        ...
    @abstractmethod
    def get_by_code(self, code: str) -> CostType | None:
        ...
    @abstractmethod
    def list(self) -> list[CostType]:
        ...
    @abstractmethod
    def update(self, cost_type: CostType) -> None:
        ...
    @abstractmethod
    def exists(self, cost_type_id: UUID) -> bool:
        ...