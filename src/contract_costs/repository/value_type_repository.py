from abc import ABC, abstractmethod
from uuid import UUID
from contract_costs.model.value_type import ValueType


class ValueTypeRepository(ABC):

    # ===== CREATE =====
    @abstractmethod
    def add(self, value_type: ValueType) -> None:
        ...

    # ===== READ =====
    @abstractmethod
    def get(
        self,
        *,
        organization_id: UUID,
        value_type_id: UUID,
    ) -> ValueType | None:
        ...

    @abstractmethod
    def get_by_code(
        self,

        organization_id: UUID,
        code: str,
    ) -> ValueType | None:
        ...

    @abstractmethod
    def list_all(
        self,
        *,
        organization_id: UUID,
    ) -> list[ValueType]:
        ...

    @abstractmethod
    def list_active(
        self,
        *,
        organization_id: UUID,
    ) -> list[ValueType]:
        ...

    # ===== UPDATE =====
    @abstractmethod
    def update(self, value_type: ValueType) -> None:
        ...

    # ===== CHECKS =====
    @abstractmethod
    def exists(
        self,
        *,
        organization_id: UUID,
        value_type_id: UUID,
    ) -> bool:
        ...
