from dataclasses import replace
from uuid import UUID

from contract_costs.model.cost_type import CostType
from contract_costs.repository.cost_type_repository import CostTypeRepository


class CostTypeService:

    def __init__(self, repository: CostTypeRepository) -> None:
        self._repository = repository

    def add(self, cost_type: CostType) -> None:
        if self._repository.get_by_code(cost_type.code):
            raise ValueError("Cost type with this code already exists")

        self._repository.add(cost_type)

    def rename(self, cost_type_id: UUID, new_name: str) -> None:
        cost_type = self._get(cost_type_id)
        updated = replace(cost_type, name=new_name)
        self._repository.update(updated)

    def deactivate(self, cost_type_id: UUID) -> None:
        cost_type = self._get(cost_type_id)
        updated = replace(cost_type, is_active=False)
        self._repository.update(updated)

    def _get(self, cost_type_id: UUID) -> CostType:
        cost_type = self._repository.get(cost_type_id)
        if cost_type is None:
            raise ValueError("Cost type does not exist")
        return cost_type
