from contract_costs.builders.cost_node_tree_builder import CostNodeTreeBuilder
from contract_costs.model.contract import Contract, ContractStarter
from contract_costs.model.cost_node import CostNode, CostNodeInput
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.services.contracts.validators.cost_node_tree_validator import CostNodeEntityValidator


class CreateContractService:

    def __init__(
        self,
        contract_repository: ContractRepository,
        cost_node_repository: CostNodeRepository,
        cost_node_tree_builder: CostNodeTreeBuilder,
        cost_node_tree_validator: CostNodeEntityValidator,
    ) -> None:
        self._contract_repository = contract_repository
        self._cost_node_repository = cost_node_repository
        self._builder = cost_node_tree_builder
        self._cost_node_tree_validator = cost_node_tree_validator
        self._contract: Contract | None = None
        self._contract_cost_nodes: list[CostNode] = []

    def init(self, contract_starter: ContractStarter) -> None:
        self._contract = Contract.from_contract_starter(contract_starter)

    def add_cost_node_tree(self, cost_node_input: list[CostNodeInput]) -> None:
        if self._contract is None:
            raise RuntimeError("Contract not initialized")
        nodes = self._builder.build(self._contract.id, cost_node_input)
        self._contract_cost_nodes.extend(nodes)

    def execute(self) -> None:
        if self._contract is None:
            raise RuntimeError("Contract not initialized")
        self._cost_node_tree_validator.validate(self._contract_cost_nodes)
        self._contract_repository.add(self._contract)
        self._cost_node_repository.add_all(self._contract_cost_nodes)

