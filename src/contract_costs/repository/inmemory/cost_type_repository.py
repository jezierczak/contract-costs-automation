from uuid import UUID
from contract_costs.model.cost_type import CostType
from contract_costs.repository.cost_type_repository import CostTypeRepository


class InMemoryCostTypeRepository(CostTypeRepository):

    def __init__(self) -> None:
        self._items: dict[UUID, CostType] = {}

    def add(self, cost_type: CostType) -> None:
        self._items[cost_type.id] = cost_type

    def get(self, cost_type_id: UUID) -> CostType | None:
        return self._items.get(cost_type_id)

    def get_by_code(self, code: str) -> CostType | None:
        return next(
            (ct for ct in self._items.values() if ct.code == code),
            None
        )

    def list(self) -> list[CostType]:
        return list(self._items.values())

    def update(self, cost_type: CostType) -> None:
        self._items[cost_type.id] = cost_type

    def exists(self, cost_type_id: UUID) -> bool:
        return cost_type_id in self._items
