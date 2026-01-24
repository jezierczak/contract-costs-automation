from uuid import UUID
from contract_costs.model.value_type import ValueType
from contract_costs.repository.value_type_repository import ValueTypeRepository


class InMemoryValueTypeRepository(ValueTypeRepository):

    def __init__(self) -> None:
        self._items: dict[UUID, ValueType] = {}

    def add(self, value_type: ValueType) -> None:
        self._items[value_type.id] = value_type

    def get(self, value_type_id: UUID) -> ValueType | None:
        return self._items.get(value_type_id)

    def get_by_code(self, code: str) -> ValueType | None:
        return next(
            (vt for vt in self._items.values() if vt.code == code),
            None
        )

    def list(self) -> list[ValueType]:
        return list(self._items.values())

    def update(self, value_type: ValueType) -> None:
        self._items[value_type.id] = value_type

    def exists(self, value_type_id: UUID) -> bool:
        return value_type_id in self._items
