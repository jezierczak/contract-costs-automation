from contract_costs.model.cost_node import CostNode
from contract_costs.repository.cost_node_repository import CostNodeRepository


class CostNodeValidator:

    def __init__(self, repository: CostNodeRepository):
        self._repository = repository

    def validate_new_node(self, node: CostNode) -> None:
        # ten sam kontrakt co parent
        # brak budżetu, jeśli parent ma budżet (polityka)
        pass

    def validate_budget_change(self, node: CostNode) -> None:
        # node z dziećmi nie może mieć budżetu
        pass

    def validate_move(self, node: CostNode) -> None:
        # brak cykli
        # zgodność kontraktu
        pass
