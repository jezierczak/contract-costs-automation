from unittest.mock import Mock

from contract_costs.services.contract_nodes.validators.contract_node_validator import (
    ContractNodeOperationValidator,
)


def test_contract_node_operation_validator_methods_are_noop() -> None:
    validator = ContractNodeOperationValidator(repository=Mock())

    validator.validate_new_node(node=Mock())
    validator.validate_budget_change(node=Mock())
    validator.validate_move(node=Mock())

