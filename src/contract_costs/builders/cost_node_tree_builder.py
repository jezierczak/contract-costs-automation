from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Iterable
from uuid import UUID,uuid4
from contract_costs.model.cost_node import CostNode
from contract_costs.model.cost_node import CostNodeInput


class CostNodeTreeBuilder(ABC):


    @abstractmethod
    def build(self,
            contract_id: UUID,
            cost_node_input: Iterable[CostNodeInput],
            *,
            existing_nodes: dict[str, CostNode] | None = None,
            root_code: str | None = None,
            root_name: str | None = None,
    ) -> list[CostNode]:
        ...


class DefaultCostNodeTreeBuilder(CostNodeTreeBuilder):
    """
       Buduje drzewo CostNode dla kontraktu.

       ZASADA:
       - Kontrakt MA ZAWSZE jeden root CostNode (techniczny)
       - Jeśli Excel zawiera wiele rootów → są pakowane pod root techniczny
       """

    def build(self,
            contract_id: UUID,
            cost_node_input: Iterable[CostNodeInput],
            *,
            existing_nodes: dict[str, CostNode] | None = None,
            root_code: str | None = None,
            root_name: str | None = None,
    ) -> list[CostNode]:

        existing_nodes = existing_nodes or {}
        cost_node_input = list(cost_node_input)

        if not cost_node_input:
            raise ValueError("At least one cost node root is required")

        technical_root_code = root_code or "ROOT"

        # ✅ 1 root i JUŻ jest ROOT → OK
        if (
                len(cost_node_input) == 1
                and cost_node_input[0]["code"] == technical_root_code
        ):
            return self._build_subtree(
                contract_id,
                cost_node_input[0],
                existing_nodes=existing_nodes,
                parent_id=None,
            )

        # ✅ KAŻDY INNY PRZYPADEK → DORABIAMY ROOT
        technical_root_input: CostNodeInput = {
            "code": technical_root_code,
            "name": root_name or "Contract root",
            "budget": self._sum_budgets(cost_node_input),
            "quantity": None,
            "unit": None,
            "is_active": True,
            "children": list(cost_node_input),
        }

        return self._build_subtree(
            contract_id,
            technical_root_input,
            existing_nodes=existing_nodes,
            parent_id=None,
        )

    # ------------------------------------------------------------------

    def _build_subtree(
            self,
            contract_id: UUID,
            node_input: CostNodeInput,
            *,
            existing_nodes: dict[str, CostNode],
            parent_id: UUID | None,
    ) -> list[CostNode]:

        code = node_input["code"]

        if code in existing_nodes:
            node_id = existing_nodes[code].id
        else:
            node_id = uuid4()

        node = CostNode(
            id=node_id,
            contract_id=contract_id,
            parent_id=parent_id,
            code=code,
            name=node_input["name"],
            budget=node_input.get("budget"),
            quantity=node_input.get("quantity"),
            unit=node_input.get("unit"),
            is_active=node_input.get("is_active", True),
        )

        nodes = [node]

        for child in node_input.get("children", []):
            nodes.extend(
                self._build_subtree(
                    contract_id,
                    child,
                    existing_nodes=existing_nodes,
                    parent_id=node_id,
                )
            )

        return nodes

    # ------------------------------------------------------------------

    def _sum_budgets(self, nodes: list[CostNodeInput]) -> Decimal | None:
        budgets = []

        for node in nodes:
            budget = node.get("budget")
            if budget is not None:
                budgets.append(budget)

            children = node.get("children") or []
            child_budget = self._sum_budgets(children)
            if child_budget is not None:
                budgets.append(child_budget)

        return sum(budgets, Decimal("0")) if budgets else None