from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Iterable
from uuid import UUID,uuid4
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.contract_node import ContractNodeInput


class ContractNodeTreeBuilder(ABC):


    @abstractmethod
    def build(self,
              contract_id: UUID,
              contract_node_input: Iterable[ContractNodeInput],
              *,
              existing_nodes: dict[str, ContractNode] | None = None,
              root_code: str | None = None,
              root_name: str | None = None,
              ) -> list[ContractNode]:
        ...


class DefaultContractNodeTreeBuilder(ContractNodeTreeBuilder):
    """
       Buduje drzewo ContractNode dla kontraktu.

       ZASADA:
       - Kontrakt MA ZAWSZE jeden root ContractNode (techniczny)
       - Jeśli Excel zawiera wiele rootów → są pakowane pod root techniczny
       """

    def build(self,
              contract_id: UUID,
              contract_node_input: Iterable[ContractNodeInput],
              *,
              existing_nodes: dict[str, ContractNode] | None = None,
              root_code: str | None = None,
              root_name: str | None = None,
              ) -> list[ContractNode]:

        existing_nodes = existing_nodes or {}
        contract_node_input = list(contract_node_input)

        if not contract_node_input:
            raise ValueError("At least one contract node root is required")

        technical_root_code = root_code or "ROOT"

        # ✅ 1 root i JUŻ jest ROOT → OK
        if (
                len(contract_node_input) == 1
                and contract_node_input[0]["code"] == technical_root_code
        ):
            return self._build_subtree(
                contract_id,
                contract_node_input[0],
                existing_nodes=existing_nodes,
                parent_id=None,
            )

        # ✅ KAŻDY INNY PRZYPADEK → DORABIAMY ROOT
        technical_root_input: ContractNodeInput = {
            "code": technical_root_code,
            "name": root_name or "Contract root",
            "budget": self._sum_budgets(contract_node_input),
            "quantity": None,
            "unit": None,
            "is_active": True,
            "children": list(contract_node_input),
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
            node_input: ContractNodeInput,
            *,
            existing_nodes: dict[str, ContractNode],
            parent_id: UUID | None,
    ) -> list[ContractNode]:

        code = node_input["code"]

        if code in existing_nodes:
            node_id = existing_nodes[code].id
        else:
            node_id = uuid4()

        existing_node = existing_nodes.get(code) #potrzebne do przepisania progressu jeśli istniał
        has_children = bool(node_input.get("children"))

        node = ContractNode(
            id=node_id,
            contract_id=contract_id,
            parent_id=parent_id,
            code=code,
            name=node_input["name"],
            budget=node_input.get("budget"),
            quantity=node_input.get("quantity"),
            unit=node_input.get("unit"),
            is_active=node_input.get("is_active", True),
            progress=(
                existing_node.progress
                if existing_node and not has_children
                else None
            ), #przepisanie progessu jeśli istniał już contract_node
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

    def _sum_budgets(self, nodes: list[ContractNodeInput]) -> Decimal | None:
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