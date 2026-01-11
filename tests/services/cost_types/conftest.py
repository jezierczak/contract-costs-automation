from uuid import UUID
from typing import Dict

import pytest

from contract_costs.model.cost_type import CostType
from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.repository.inmemory.cost_type_repository import InMemoryCostTypeRepository


# class InMemoryCostTypeRepository(CostTypeRepository):
#     def __init__(self) -> None:
#         self._data: Dict[UUID, CostType] = {}
#
#     def add(self, cost_type: CostType) -> None:
#         self._data[cost_type.id] = cost_type
#
#     def get(self, cost_type_id: UUID) -> CostType | None:
#         return self._data.get(cost_type_id)
#
#     def get_by_code(self, code: str) -> CostType | None:
#         for ct in self._data.values():
#             if ct.code == code:
#                 return ct
#         return None
#
#     def list(self) -> list[CostType]:
#         return list(self._data.values())
#
#     def update(self, cost_type: CostType) -> None:
#         self._data[cost_type.id] = cost_type
#
#     def exists(self, cost_type_id: UUID) -> bool:
#         return cost_type_id in self._data
#

@pytest.fixture
def repo():
    return InMemoryCostTypeRepository()
