from dataclasses import replace
from datetime import datetime
import logging
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.services.contracts.apply.command.update_contract_structure_command import UpdateContractStructureCommand
from contract_costs.services.contracts.builders.contract_node_tree_builder import ContractNodeTreeBuilder
from contract_costs.services.contracts.validators.contract_node_tree_validator import ContractNodeEntityValidator
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class UpdateContractStructureService(ActionHandler[UpdateContractStructureCommand, None]):

    def __init__(
        self,
        # contract_repository: ContractRepository,
        # contract_node_repository: ContractNodeRepository,
        contract_node_tree_builder: ContractNodeTreeBuilder,
        contract_node_tree_validator: ContractNodeEntityValidator,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        # self._contract_repository = contract_repository
        # self._contract_node_repository = contract_node_repository
        self._builder = contract_node_tree_builder
        self._contract_node_tree_validator = contract_node_tree_validator
        self._clock = clock

    def execute(self, *, action: UpdateContractStructureCommand, uow: UnitOfWork) -> None:

        contract_repo = uow.contracts
        node_repo = uow.contract_nodes

        logger.info(
            "Updating contract structure: contract_id=%s, nodes_in_excel=%d",
            action.contract_id,
            len(action.contract_node_input),
        )

        contract = self._get_contract(
            contract_repo=contract_repo,
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )

        updated_contract = replace(
            contract,
            name=action.name,
            description=action.description,
            start_date=action.start_date,
            end_date=action.end_date,
            budget=action.budget,
            status=action.status,
            path=action.path,
            updated_at=self._clock(),
            updated_by_user_id=action.actor_user_id,
        )

        existing_nodes = node_repo.list_by_contract(
            contract_id=action.contract_id,
            organization_id=action.organization_id,
        )

        if not node_repo.has_values(
            contract_id=action.contract_id,
            organization_id=action.organization_id,
        ):
            self._replace_structure_hard(action=action,node_repo=node_repo)
        else:
            self._replace_structure_safe(action=action, existing_nodes=existing_nodes,node_repo=node_repo)

        contract_repo.update(updated_contract)

    def _replace_structure_hard(self, *, action: UpdateContractStructureCommand,node_repo:ContractNodeRepository) -> None:
        node_repo.delete_by_contract(
            contract_id=action.contract_id,
            organization_id=action.organization_id,
        )

        new_nodes = self._builder.build(
            organization_id=action.organization_id,
            actor_user_id=action.actor_user_id,
            created_at=self._clock(),
            contract_id=action.contract_id,
            contract_node_input=action.contract_node_input,
        )

        self._contract_node_tree_validator.validate(new_nodes)
        node_repo.add_all(new_nodes)

    def _replace_structure_safe(
        self,
        *,
        node_repo:ContractNodeRepository,
        action: UpdateContractStructureCommand,
        existing_nodes: list[ContractNode],
    ) -> None:
        existing_by_code = {n.code: n for n in existing_nodes}

        new_nodes = self._builder.build(
            organization_id=action.organization_id,
            actor_user_id=action.actor_user_id,
            created_at=self._clock(),
            contract_id=action.contract_id,
            contract_node_input=action.contract_node_input,
            existing_nodes=existing_by_code,
        )

        self._contract_node_tree_validator.validate(new_nodes)

        new_by_code = {n.code: n for n in new_nodes}
        to_update = []
        to_insert = []
        to_delete = []

        for code, node in new_by_code.items():
            if code in existing_by_code:
                to_update.append(node)
            else:
                to_insert.append(node)

        for code, old_node in existing_by_code.items():
            if code not in new_by_code:
                if node_repo.node_has_values(
                    contract_node_id=old_node.id,
                    organization_id=action.organization_id,
                ):
                    raise ValueError(f"Cannot remove contract node '{code}' - costs already exist")
                to_delete.append(old_node.id)

        if to_delete:
            node_repo.delete_many(
                ids=to_delete,
                organization_id=action.organization_id,
            )

        if to_update:
            node_repo.update_many(to_update)

        if to_insert:
            node_repo.add_all(to_insert)
    @staticmethod
    def _get_contract( *, organization_id: UUID, contract_id: UUID,contract_repo:ContractRepository) -> Contract:
        contract = contract_repo.get(
            organization_id=organization_id,
            contract_id=contract_id,
        )
        if contract is None:
            raise ValueError("Contract does not exist")
        return contract
