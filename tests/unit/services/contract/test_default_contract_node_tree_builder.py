import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime



from contract_costs.common.time import utc_now
from contract_costs.model.contract_node import ContractNode
from contract_costs.services.contracts.builders.contract_node_tree_builder import DefaultContractNodeTreeBuilder
from tests.helpers.contracts_helpers import make_node_input


# --------------------------------------------------
# HELPERS
# --------------------------------------------------



# --------------------------------------------------
# BASIC VALIDATION
# --------------------------------------------------

def test_empty_input_raises():
    builder = DefaultContractNodeTreeBuilder()

    with pytest.raises(ValueError):
        builder.build(
            contract_id=uuid4(),
            organization_id=uuid4(),
            actor_user_id=None,
            created_at=utc_now(),
            contract_node_input=[],
        )


# --------------------------------------------------
# AUTO ROOT CREATION
# --------------------------------------------------

def test_auto_root_created_when_multiple_roots():
    builder = DefaultContractNodeTreeBuilder()

    input_data = [
        make_node_input(code="1", budget=Decimal("100")),
        make_node_input(code="2", budget=Decimal("200")),
    ]

    nodes = builder.build(
        contract_id=uuid4(),
        organization_id=uuid4(),
        actor_user_id=None,
        created_at=utc_now(),
        contract_node_input=input_data,
    )

    # powinien powstać ROOT + 2 dzieci
    assert len(nodes) == 3

    root = next(n for n in nodes if n.parent_id is None)
    assert root.code == "ROOT"
    assert root.budget == Decimal("300")


# --------------------------------------------------
# SINGLE ROOT PASSTHROUGH
# --------------------------------------------------

def test_single_root_with_code_root_is_not_wrapped():
    builder = DefaultContractNodeTreeBuilder()

    input_data = [
        make_node_input(
            code="ROOT",
            budget=Decimal("500"),
            children=[
                make_node_input(code="1", budget=Decimal("100"))
            ]
        )
    ]

    nodes = builder.build(
        contract_id=uuid4(),
        organization_id=uuid4(),
        actor_user_id=None,
        created_at=utc_now(),
        contract_node_input=input_data,
    )

    # ROOT + child
    assert len(nodes) == 2

    root = next(n for n in nodes if n.parent_id is None)
    assert root.code == "ROOT"
    assert root.budget == Decimal("500")


# --------------------------------------------------
# PARENT RELATIONS
# --------------------------------------------------

def test_parent_ids_are_set_correctly():
    builder = DefaultContractNodeTreeBuilder()

    input_data = [
        make_node_input(
            code="A",
            children=[
                make_node_input(code="B"),
            ],
        )
    ]

    nodes = builder.build(
        contract_id=uuid4(),
        organization_id=uuid4(),
        actor_user_id=None,
        created_at=utc_now(),
        contract_node_input=input_data,
    )

    root = next(n for n in nodes if n.parent_id is None)
    child = next(n for n in nodes if n.parent_id == root.id)

    assert child.code == "A" or child.code == "B"


# --------------------------------------------------
# EXISTING NODE REUSE
# --------------------------------------------------

def test_existing_node_preserves_id_and_created_fields():
    builder = DefaultContractNodeTreeBuilder()

    existing_id = uuid4()

    existing_node = ContractNode(
        id=existing_id,
        organization_id=uuid4(),
        contract_id=uuid4(),
        parent_id=None,
        code="A",
        name="Old",
        budget=Decimal("100"),
        quantity=None,
        unit=None,
        is_active=True,
        created_at=datetime(2020, 1, 1),
        created_by_user_id=uuid4(),
        updated_at=None,
        updated_by_user_id=None,
        progress_history={},
    )

    input_data = [make_node_input(code="A", budget=Decimal("200"))]

    nodes = builder.build(
        contract_id=existing_node.contract_id,
        organization_id=existing_node.organization_id,
        actor_user_id=uuid4(),
        created_at=utc_now(),
        contract_node_input=input_data,
        existing_nodes={"A": existing_node},
    )

    node = next(n for n in nodes if n.code == "A")

    assert node.id == existing_id
    assert node.created_at == existing_node.created_at
    assert node.updated_at is not None


# --------------------------------------------------
# SUM BUDGET RECURSIVE
# --------------------------------------------------

def test_sum_budgets_recursive():
    builder = DefaultContractNodeTreeBuilder()

    input_data = [
        make_node_input(
            code="A",
            children=[
                make_node_input(code="B", budget=Decimal("100")),
                make_node_input(code="C", budget=Decimal("200")),
            ],
        )
    ]

    nodes = builder.build(
        contract_id=uuid4(),
        organization_id=uuid4(),
        actor_user_id=None,
        created_at=utc_now(),
        contract_node_input=input_data,
    )

    root = next(n for n in nodes if n.parent_id is None)

    assert root.budget == Decimal("300")
