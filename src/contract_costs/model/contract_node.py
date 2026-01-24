from  dataclasses import dataclass
from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from contract_costs.model.unit_of_measure import UnitOfMeasure


class ContractNodeInput(TypedDict):
    code: str
    name: str
    budget: Decimal | None
    quantity: Decimal | None
    unit: UnitOfMeasure | None
    children: list["ContractNodeInput"]
    is_active: bool


@dataclass
class ContractNode:
    id: UUID
    contract_id: UUID
    code: str
    name: str
    parent_id: UUID | None
    quantity: Decimal | None
    unit: UnitOfMeasure | None
    budget: Decimal | None
    is_active: bool



    @staticmethod
    def calculate_budget_from_leaves(
        node_id: UUID,
        nodes_by_parent: dict[UUID | None, list["ContractNode"]],
    ) -> Decimal:
        children = [
            c for c in nodes_by_parent.get(node_id, [])
            if c.is_active
        ]

        # 1 jeśli są aktywne dzieci → liczymy TYLKO dzieci
        if children:
            total = Decimal("0")
            for child in children:
                total += ContractNode.calculate_budget_from_leaves(
                    child.id, nodes_by_parent
                )
            return total

        # 2 jeśli brak dzieci → liść → jego własny budżet
        node = next(
            n
            for nodes in nodes_by_parent.values()
            for n in nodes
            if n.id == node_id
        )

        return node.budget or Decimal("0")
