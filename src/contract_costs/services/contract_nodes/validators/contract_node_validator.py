from contract_costs.model.contract_node import ContractNode
from contract_costs.repository.contract_node_repository import ContractNodeRepository


class ContractNodeOperationValidator:

    def __init__(self, repository: ContractNodeRepository):
        self._repository = repository

    def validate_new_node(self, node: ContractNode) -> None:
        # ten sam kontrakt co parent
        # brak budżetu, jeśli parent ma budżet (polityka)
        pass

    def validate_budget_change(self, node: ContractNode) -> None:
        # node z dziećmi nie może mieć budżetu
        pass

    def validate_move(self, node: ContractNode) -> None:
        # brak cykli
        # zgodność kontraktu
        pass
