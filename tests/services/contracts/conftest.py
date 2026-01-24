import uuid
from decimal import Decimal

import pytest

from contract_costs.model.contract_node import ContractNode


@pytest.fixture
def simple_tree_nodes() -> list[ContractNode]:
    contract_id = uuid.uuid4()

    root = ContractNode(
        id=uuid.uuid4(),
        contract_id=contract_id,
        parent_id=None,
        code="ROOT",
        name="Root",
        budget=None,
        quantity=None,
        unit=None,
        is_active=True,
        progress=None,
    )

    a = ContractNode(
        id=uuid.uuid4(),
        contract_id=contract_id,
        parent_id=root.id,
        code="A",
        name="A",
        budget=None,
        quantity=None,
        unit=None,
        is_active=True,
        progress=None,
    )

    a1 = ContractNode(
        id=uuid.uuid4(),
        contract_id=contract_id,
        parent_id=a.id,
        code="A1",
        name="A1",
        budget=Decimal("100"),
        quantity=None,
        unit=None,
        is_active=True,
        progress=Decimal("0.5"),
    )

    a2 = ContractNode(
        id=uuid.uuid4(),
        contract_id=contract_id,
        parent_id=a.id,
        code="A2",
        name="A2",
        budget=Decimal("200"),
        quantity=None,
        unit=None,
        is_active=True,
        progress=Decimal("0.25"),
    )

    b = ContractNode(
        id=uuid.uuid4(),
        contract_id=contract_id,
        parent_id=root.id,
        code="B",
        name="B",
        budget=Decimal("300"),
        quantity=None,
        unit=None,
        is_active=True,
        progress=Decimal("1.0"),
    )

    return [root, a, a1, a2, b]
