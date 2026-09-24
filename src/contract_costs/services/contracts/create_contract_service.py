from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode, ContractNodeInput
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.services.contracts.builders.contract_node_tree_builder import ContractNodeTreeBuilder
from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand
from contract_costs.services.contracts.validators.contract_node_tree_validator import ContractNodeEntityValidator
from contract_costs.unit_of_work import UnitOfWork


class CreateContractService(ActionHandler[CreateContractCommand, Contract]):

    def __init__(
        self,
        # contract_repository: ContractRepository,
        # contract_node_repository: ContractNodeRepository,
        contract_node_tree_builder: ContractNodeTreeBuilder,
        contract_node_tree_validator: ContractNodeEntityValidator,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        # self._contract_repository = contract_repository
        # self._contract_node_repository = contract_node_repository
        self._builder = contract_node_tree_builder
        self._validator = contract_node_tree_validator
        self._id_generator = id_generator
        self._clock = clock

    def execute(
        self,
        *,
        action: CreateContractCommand,
        uow:UnitOfWork,
    ) -> Contract:

        Contract.validate_dates(action.start_date, action.end_date)

        now = self._clock()
        contract_id = self._id_generator()

        contract = Contract(
            id=contract_id,
            organization_id=action.organization_id,
            created_at=now,
            created_by_user_id=action.actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
            code=action.code,
            name=action.name,
            owner=action.owner,
            client=action.client,
            description=action.description,
            start_date=action.start_date,
            end_date=action.end_date,
            budget=action.budget,
            path=action.path,
            status=action.status,
            contract_type=action.contract_type,
        )

        nodes: list[ContractNode] = []
        contract_node_input: list[ContractNodeInput] = action.contract_node_input or []

        if contract_node_input:
            nodes = self._builder.build(
                contract_id=contract.id,
                organization_id=contract.organization_id,
                actor_user_id=action.actor_user_id,
                created_at=now,
                contract_node_input=contract_node_input,
            )

            self._validator.validate(nodes)

        uow.contracts.add(contract)

        if nodes:
            uow.contract_nodes.add_all(nodes)

        return contract
