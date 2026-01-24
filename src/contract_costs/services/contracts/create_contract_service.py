from contract_costs.builders.contract_node_tree_builder import ContractNodeTreeBuilder
from contract_costs.model.contract import Contract, ContractStarter
from contract_costs.model.contract_node import ContractNode, ContractNodeInput
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
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
    ) -> None:
        self._contract_repository = contract_repository
        self._contract_node_repository = contract_node_repository
        self._builder = contract_node_tree_builder
        self._contract_node_tree_validator = contract_node_tree_validator
        self._contract: Contract | None = None
        self._contract_nodes: list[ContractNode] = []

    def init(self, contract_starter: ContractStarter) -> None:
        self._contract = Contract.from_contract_starter(contract_starter)
        logger.info(
            "Initializing contract: code=%s, name=%s",
            contract_starter['code'],
            contract_starter['name'],
        )

    def add_contract_node_tree(self, contract_node_input: list[ContractNodeInput]) -> None:
        if self._contract is None:
            raise RuntimeError("Contract not initialized")
        nodes = self._builder.build(self._contract.id, contract_node_input)
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

