import uuid
from decimal import Decimal

import pytest

from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode
from contract_costs.repository.inmemory.contract_node_repository import InMemoryContractNodeRepository
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository
from contract_costs.repository.inmemory.snapshot.contract_node_snapshot_repository import \
    InMemoryContractNodeSnapshotRepository
from contract_costs.repository.inmemory.snapshot.contract_node_value_snapshot_repository import \
    InMemoryContractNodeValueSnapshotRepository
from contract_costs.repository.inmemory.snapshot.contract_snapshot_repository import InMemoryContractSnapshotRepository

@pytest.fixture
def contract_and_nodes():
    contract_id = uuid.uuid4()

    contract = Contract(
        id=contract_id,
        code="TEST",
        name="Test",
        status=None,
        owner=None,
        client=None,
        start_date=None,
        end_date=None,
        budget=None,
        path=None,
        description="TeST"
    )

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

    return contract, [root, a, a1, a2]

@pytest.fixture
def repos(contract_and_nodes):
    contract, nodes = contract_and_nodes

    contract_repo = InMemoryContractRepository()
    contract_repo.add(contract)

    node_repo = InMemoryContractNodeRepository()
    node_repo.add_all(nodes)

    invoice_repo = InMemoryInvoiceLineRepository()

    snapshot_repo = InMemoryContractSnapshotRepository()
    node_snapshot_repo = InMemoryContractNodeSnapshotRepository()
    value_snapshot_repo = InMemoryContractNodeValueSnapshotRepository()

    return (
        contract,
        contract_repo,
        node_repo,
        invoice_repo,
        snapshot_repo,
        node_snapshot_repo,
        value_snapshot_repo,
    )
