from abc import ABC, abstractmethod
from uuid import UUID
from contract_costs.model.value_type import (ValueType)

class ValueTypeRepository(ABC):
    @abstractmethod
    def add(self, value_type: ValueType) -> None:
        ...
    @abstractmethod
    def get(self, value_type_id: UUID) -> ValueType | None:
        ...
    @abstractmethod
    def get_by_code(self, code: str) -> ValueType | None:
        ...
    @abstractmethod
    def list(self) -> list[ValueType]:
        ...
    @abstractmethod
    def update(self, value_type: ValueType) -> None:
        ...
    @abstractmethod
    def exists(self, value_type_id: UUID) -> bool:
        ...