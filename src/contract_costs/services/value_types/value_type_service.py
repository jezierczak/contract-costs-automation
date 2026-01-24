from dataclasses import replace
from uuid import UUID

from contract_costs.model.value_type import ValueType
from contract_costs.repository.value_type_repository import ValueTypeRepository


class ValueTypeService:

    def __init__(self, repository: ValueTypeRepository) -> None:
        self._repository = repository

    def add(self, value_type: ValueType) -> None:
        if self._repository.get_by_code(value_type.code):
            raise ValueError("Value type with this code already exists")

        self._repository.add(value_type)

    def rename(self, value_type_id: UUID, new_name: str) -> None:
        value_type = self._get(value_type_id)
        updated = replace(value_type, name=new_name)
        self._repository.update(updated)

    def deactivate(self, value_type_id: UUID) -> None:
        value_type = self._get(value_type_id)
        updated = replace(value_type, is_active=False)
        self._repository.update(updated)

    def _get(self, value_type_id: UUID) -> ValueType:
        value_type = self._repository.get(value_type_id)
        if value_type is None:
            raise ValueError("Value type does not exist")
        return value_type
