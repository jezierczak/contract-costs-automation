from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Callable
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.contract_node import ContractNodeInput


class ContractNodeTreeBuilder(ABC):


    @abstractmethod
    def build(
            self,
            *,
            contract_id: UUID,
            organization_id: UUID,
            actor_user_id: UUID | None,
            created_at: datetime,
            contract_node_input: list[ContractNodeInput],
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

    def build(
            self,
            *,
            contract_id: UUID,
            organization_id: UUID,
            actor_user_id: UUID | None,
            created_at: datetime,
            contract_node_input: list[ContractNodeInput],
            existing_nodes: dict[str, ContractNode] | None = None,
            root_code: str | None = None,
            root_name: str | None = None,
            id_generator: Callable[[], UUID] = new_uuid,
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
                contract_id=contract_id,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                created_at_param=created_at,
                node_input=contract_node_input[0],
                existing_nodes=existing_nodes,
                parent_id=None,
                id_generator=id_generator
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
            contract_id=contract_id,
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            created_at_param=created_at,
            node_input=technical_root_input,
            existing_nodes=existing_nodes,
            parent_id=None,
            id_generator=id_generator
        )

    # ------------------------------------------------------------------

    def _build_subtree(
            self,
            *,
            contract_id: UUID,
            organization_id: UUID,
            actor_user_id: UUID | None,
            created_at_param: datetime,
            node_input: ContractNodeInput,
            existing_nodes: dict[str, ContractNode],
            parent_id: UUID | None,
            id_generator: Callable[[], UUID]
    ) -> list[ContractNode]:

        code = node_input["code"]

        existing = existing_nodes.get(code)

        if existing:
            node_id = existing_nodes[code].id
            created_at = existing.created_at
            created_by_user_id = existing.created_by_user_id

            updated_at = created_at_param  # to co przyszło z serwisu
            updated_by_user_id = actor_user_id
        else:
            node_id = id_generator()
            created_at = created_at_param
            created_by_user_id = actor_user_id
            updated_at = None
            updated_by_user_id = None

        # existing_node = existing_nodes.get(code) #potrzebne do przepisania progressu jeśli istniał
        # has_children = bool(node_input.get("children"))

        node = ContractNode(
            id=node_id,
            organization_id=organization_id,
            contract_id=contract_id,
            parent_id=parent_id,
            code=code,
            name=node_input["name"],
            budget=node_input.get("budget"),
            quantity=node_input.get("quantity"),
            unit=node_input.get("unit"),
            is_active=node_input.get("is_active", True),
            created_at=created_at,
            created_by_user_id=created_by_user_id,
            updated_at=updated_at,
            updated_by_user_id=updated_by_user_id,
            progress_history={},
        )

        nodes = [node]

        for child in node_input.get("children", []):
            nodes.extend(
                self._build_subtree(
                    contract_id=contract_id,
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    created_at_param=created_at_param,
                    node_input=child,
                    existing_nodes=existing_nodes,
                    parent_id=node_id,
                    id_generator=id_generator
                )
            )

        return nodes

    # ------------------------------------------------------------------

    def _sum_budgets(self, nodes: list[ContractNodeInput]) -> Decimal | None:
        total = Decimal("0")
        found = False

        for node in nodes:
            children = node.get("children") or []

            if children:
                child_sum = self._sum_budgets(children)
                if child_sum is not None:
                    total += child_sum
                    found = True
            else:
                budget = node.get("budget")
                if budget is not None:
                    total += budget
                    found = True

        return total if found else None
