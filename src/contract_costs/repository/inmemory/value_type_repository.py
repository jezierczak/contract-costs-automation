from uuid import UUID
from contract_costs.model.value_type import ValueType
from contract_costs.repository.value_type_repository import ValueTypeRepository


class InMemoryValueTypeRepository(ValueTypeRepository):

    def __init__(self) -> None:
        self._items: dict[UUID, ValueType] = {}

    def add(self, value_type: ValueType) -> None:
        self._items[value_type.id] = value_type

    def get(
        self,
        *,
        organization_id: UUID,
        value_type_id: UUID,
    ) -> ValueType | None:
        vt = self._items.get(value_type_id)
        if not vt or vt.organization_id != organization_id:
            return None
        return vt

    def get_by_code(
        self,
        organization_id: UUID,
        code: str,
    ) -> ValueType | None:
        for vt in self._items.values():
            if vt.organization_id == organization_id and vt.code == code:
                return vt
        return None

    def list_all(
        self,
        *,
        organization_id: UUID,
    ) -> list[ValueType]:
        return [
            vt for vt in self._items.values()
            if vt.organization_id == organization_id
        ]

    def list_active(
        self,
        *,
        organization_id: UUID,
    ) -> list[ValueType]:
        return [
            vt for vt in self._items.values()
            if vt.organization_id == organization_id and vt.is_active
        ]

    def update(self, value_type: ValueType) -> None:
        self._items[value_type.id] = value_type

    def exists(
        self,
        *,
        organization_id: UUID,
        value_type_id: UUID,
    ) -> bool:
        vt = self._items.get(value_type_id)
        return bool(vt and vt.organization_id == organization_id)
