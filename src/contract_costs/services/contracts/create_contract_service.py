from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.builders.contract_node_tree_builder import ContractNodeTreeBuilder
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode, ContractNodeInput
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand
from contract_costs.services.contracts.validators.contract_node_tree_validator import ContractNodeEntityValidator
import logging

logger = logging.getLogger(__name__)

class CreateContractService:

    def __init__(
        self,
        contract_repository: ContractRepository,
        contract_node_repository: ContractNodeRepository,
        contract_node_tree_builder: ContractNodeTreeBuilder,
        contract_node_tree_validator: ContractNodeEntityValidator,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._contract_repository = contract_repository
        self._contract_node_repository = contract_node_repository
        self._builder = contract_node_tree_builder
        self._contract_node_tree_validator = contract_node_tree_validator
        self._id_generator = id_generator
        self._clock = clock

        self._contract: Contract | None = None
        self._contract_nodes: list[ContractNode] = []

    def init(self, command: CreateContractCommand) -> None:
        now = self._clock()
        contract_id = self._id_generator()

        self._contract = Contract(
            id=contract_id,
            organization_id=command.organization_id,
            created_at=now,
            created_by_user_id=command.actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
            code=command.code,
            name=command.name,
            owner=command.owner,
            client=command.client,
            description=command.description,
            start_date=command.start_date,
            end_date=command.end_date,
            budget=command.budget,
            path=command.path,
            status=command.status,
        )
        logger.info(
            "Initializing contract: code=%s, name=%s",
            self._contract.code,
            self._contract.name
        )

    def add_contract_node_tree(self, contract_node_input: list[ContractNodeInput]) -> None:

        now = self._clock()

        if self._contract is None:
            raise RuntimeError("Contract not initialized")
        nodes = self._builder.build(
            contract_id=self._contract.id,
            organization_id=self._contract.organization_id,
            actor_user_id=self._contract.created_by_user_id,
            created_at=now,
            contract_node_input=contract_node_input,
        )
        logger.info(
            "Adding contract node tree to contract_id=%s, nodes=%d",
            self._contract.id,
            len(contract_node_input),
        )
        self._contract_nodes.extend(nodes)

    def execute(self) -> None:
        if self._contract is None:
            raise RuntimeError("Contract not initialized")
        logger.debug(
            "Validating contract node tree for contract_id=%s",
            self._contract.id,
        )
        if self._contract_nodes:
            self._contract_node_tree_validator.validate(self._contract_nodes)
        else:
            logger.info(
                "Contract %s created without cost nodes (CLI mode)",
                self._contract.id,
            )
        self._contract_repository.add(self._contract)
        self._contract_node_repository.add_all(self._contract_nodes)
        logger.info(
            "Contract created successfully: id=%s, contract_nodes=%d",
            self._contract.id,
            len(self._contract_nodes),
        )

