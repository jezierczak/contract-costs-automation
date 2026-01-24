from uuid import UUID
from dataclasses import replace
from decimal import Decimal

from contract_costs.model.contract_node import ContractNode
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.services.contract_nodes.validators.contract_node_validator import ContractNodeOperationValidator


class ContractNodeService:

    def __init__(
        self,
        repository: ContractNodeRepository,
        validator: ContractNodeOperationValidator,
    ) -> None:
        self._repository = repository
        self._validator = validator


    def add_node(self, node: ContractNode) -> None:
        """
        Add new contract node to contract structure.
        """

        if self._repository.exists(node.id):
            raise ValueError("Contract node already exists")

        if node.parent_id is not None:
            parent = self._repository.get(node.parent_id)
            if parent is None:
                raise ValueError("Parent contract node does not exist")

        self._validator.validate_new_node(node)

        self._repository.add(node)


    def update_budget(
        self,
        node_id: UUID,
        budget: Decimal | None
    ) -> None:
        """
        Update budget for given contract node.
        """

        node = self._repository.get(node_id)
        if node is None:
            raise ValueError("contract node does not exist")

        updated = replace(node, budget=budget)

        self._validator.validate_budget_change(updated)

        self._repository.update(updated)

    def move_node(
        self,
        node_id: UUID,
        new_parent_id: UUID | None
    ) -> None:
        """
        Move contract node under new parent.
        """

        node = self._repository.get(node_id)
        if node is None:
            raise ValueError("contract node does not exist")

        if new_parent_id is not None:
            new_parent = self._repository.get(new_parent_id)
            if new_parent is None:
                raise ValueError("New parent contract node does not exist")

        updated = replace(node, parent_id=new_parent_id)

        self._validator.validate_move(updated)

        self._repository.update(updated)

    def deactivate_node(self, node_id: UUID) -> None:
        """
        Deactivate contract node (soft delete).
        """

        node = self._repository.get(node_id)
        if node is None:
            raise ValueError("Contract node does not exist")

        updated = replace(node, is_active=False)

        self._repository.update(updated)

