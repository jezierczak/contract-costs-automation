from dataclasses import dataclass, field
from datetime import date
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
    # progress: Decimal | None  # zakres 0.0 – 1.0
    is_active: bool

    progress_history: dict[date, Decimal]

    @property
    def progress(self) -> Decimal | None:
        if not self.progress_history:
            return None
        latest_date = max(self.progress_history.keys())
        return self.progress_history[latest_date]

    def progress_at(self, at_date: date) -> Decimal | None:
        """
        Zwraca progress obowiązujący NA DANY DZIEŃ.
        (ostatni zapis <= at_date)
        """
        if not self.progress_history:
            return None

        applicable_dates = [
            d for d in self.progress_history.keys()
            if d <= at_date
        ]

        if not applicable_dates:
            return None

        latest_date = max(applicable_dates)
        return self.progress_history[latest_date]

    def has_progress(self) -> bool:
        return bool(self.progress_history)

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

    def is_leaf(self, nodes_by_parent: dict[UUID | None, list["ContractNode"]]) -> bool:
        return len(nodes_by_parent.get(self.id, [])) == 0

    def can_have_progress(self, nodes_by_parent: dict[UUID | None, list["ContractNode"]]) -> bool:
        return self.is_active and self.is_leaf(nodes_by_parent)

    @staticmethod
    def calculate_progress_from_leaves(
            node_id: UUID,
            nodes_by_parent: dict[UUID | None, list["ContractNode"]],
    ) -> Decimal | None:
        children = [
            c for c in nodes_by_parent.get(node_id, [])
            if c.is_active
        ]

        # jeśli są dzieci → liczmy z dzieci
        if children:
            weighted_sum = Decimal("0")
            total_budget = Decimal("0")

            for child in children:
                child_progress = ContractNode.calculate_progress_from_leaves(
                    child.id, nodes_by_parent
                )
                if child_progress is None or child.budget is None:
                    continue

                weighted_sum += child_progress * child.budget
                total_budget += child.budget

            if total_budget == 0:
                return None

            return weighted_sum / total_budget

        # liść
        node = next(
            n
            for nodes in nodes_by_parent.values()
            for n in nodes
            if n.id == node_id
        )

        return node.progress

    @staticmethod
    def calculate_progress_from_leaves_at(
            node_id: UUID,
            nodes_by_parent: dict[UUID | None, list["ContractNode"]],
            at_date: date,
    ) -> Decimal | None:
        children = [
            c for c in nodes_by_parent.get(node_id, [])
            if c.is_active
        ]

        if children:
            weighted_sum = Decimal("0")
            total_budget = Decimal("0")

            for child in children:
                child_progress = ContractNode.calculate_progress_from_leaves_at(
                    child.id, nodes_by_parent, at_date
                )

                if child_progress is None or child.budget is None:
                    continue

                weighted_sum += child_progress * child.budget
                total_budget += child.budget

            if total_budget == 0:
                return None

            return weighted_sum / total_budget

        # liść
        node = next(
            n
            for nodes in nodes_by_parent.values()
            for n in nodes
            if n.id == node_id
        )

        return node.progress_at(at_date)