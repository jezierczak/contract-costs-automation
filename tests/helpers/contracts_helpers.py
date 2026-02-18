from decimal import Decimal
from uuid import uuid4, UUID

from contract_costs.common.time import utc_now
from contract_costs.model.contract_node import ContractNodeInput, ContractNode
from contract_costs.services.contracts.builders.contract_node_tree_builder import ContractNodeTreeBuilder
from contract_costs.services.contracts.validators.contract_node_tree_validator import ContractNodeEntityValidator


class FakeContractNodeTreeBuilder(ContractNodeTreeBuilder):
    def __init__(self, nodes_to_return):
        self.nodes_to_return = nodes_to_return
        self.called = False

    def build(
        self,
        *,
        contract_id,
        organization_id,
        actor_user_id,
        created_at,
        contract_node_input,
        existing_nodes: dict[str, ContractNode] | None = None,
        root_code: str | None = None,
        root_name: str | None = None,
    ):
        self.called = True
        for node in self.nodes_to_return:
            node.contract_id = contract_id
            node.organization_id = organization_id

        return self.nodes_to_return

class FakeValidator(ContractNodeEntityValidator):
    def __init__(self, should_fail: bool = False):
        self.called = False
        self.should_fail = should_fail

    def validate(self, nodes: list[ContractNode]) -> None:
        self.called = True
        if self.should_fail:
            raise ValueError("Invalid tree")

def make_contract_node(
    *,
    organization_id: UUID,
    contract_id: UUID,
    code: str = "1",
    budget: Decimal | None = Decimal("100"),
    parent_id: UUID | None = None,
    is_active: bool = True,
) -> ContractNode:

    now = utc_now()

    return ContractNode(
        id=uuid4(),
        organization_id=organization_id,
        created_at=now,
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,

        contract_id=contract_id,
        code=code,
        name=f"Node {code}",
        parent_id=parent_id,
        quantity=None,
        unit=None,
        budget=budget,
        is_active=is_active,
        progress_history={},
    )



def make_node_input(
    *,
    code: str,
    name: str | None = None,
    budget: Decimal | None = Decimal("100"),
    children: list[ContractNodeInput] | None = None,
    is_active: bool = True,
) -> ContractNodeInput:
    return {
        "code": code,
        "name": name or f"Node {code}",
        "budget": budget,
        "quantity": None,
        "unit": None,
        "children": children or [],
        "is_active": is_active,
    }

