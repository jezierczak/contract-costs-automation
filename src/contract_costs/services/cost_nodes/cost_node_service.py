from uuid import UUID
from dataclasses import replace
from decimal import Decimal

from contract_costs.model.cost_node import CostNode
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.services.cost_nodes.validators.cost_node_validator import CostNodeOperationValidator


class CostNodeService:

    def __init__(
        self,
        repository: CostNodeRepository,
        validator: CostNodeOperationValidator,
    ) -> None:
        self._repository = repository
        self._validator = validator


    def add_node(self, node: CostNode) -> None:
        """
        Add new cost node to contract structure.
        """

        if self._repository.exists(node.id):
            raise ValueError("Cost node already exists")

        if node.parent_id is not None:
            parent = self._repository.get(node.parent_id)
            if parent is None:
                raise ValueError("Parent cost node does not exist")

        self._validator.validate_new_node(node)

        self._repository.add(node)


    def update_budget(
        self,
        node_id: UUID,
        budget: Decimal | None
    ) -> None:
        """
        Update budget for given cost node.
        """

        node = self._repository.get(node_id)
        if node is None:
            raise ValueError("Cost node does not exist")

        updated = replace(node, budget=budget)

        self._validator.validate_budget_change(updated)

        self._repository.update(updated)

    def move_node(
        self,
        node_id: UUID,
        new_parent_id: UUID | None
    ) -> None:
        """
        Move cost node under new parent.
        """

        node = self._repository.get(node_id)
        if node is None:
            raise ValueError("Cost node does not exist")

        if new_parent_id is not None:
            new_parent = self._repository.get(new_parent_id)
            if new_parent is None:
                raise ValueError("New parent cost node does not exist")

        updated = replace(node, parent_id=new_parent_id)

        self._validator.validate_move(updated)

        self._repository.update(updated)

    def deactivate_node(self, node_id: UUID) -> None:
        """
        Deactivate cost node (soft delete).
        """

        node = self._repository.get(node_id)
        if node is None:
            raise ValueError("Cost node does not exist")

        updated = replace(node, is_active=False)

        self._repository.update(updated)

