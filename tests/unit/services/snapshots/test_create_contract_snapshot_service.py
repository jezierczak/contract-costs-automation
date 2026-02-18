from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.contract_node import ContractNode
from contract_costs.services.snapshots.create_contract_snapshot_service import (
    CreateContractSnapshotService,
)
from contract_costs.services.snapshots.dto.create_contract_snapshot_command import (
    CreateContractSnapshotCommand,
)
from tests.builders.contract_builder import ContractBuilder
from tests.builders.contract_snapshot_builder import ContractSnapshotBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from tests.helpers.contracts_helpers import make_contract_node


class _FakeUow:
    def __init__(
        self,
        *,
        contract_repo,
        node_repo,
        line_repo,
        snapshot_repo,
        node_snapshot_repo,
        value_snapshot_repo,
    ):
        self.contracts = contract_repo
        self.contract_nodes = node_repo
        self.financial_record_lines = line_repo
        self.contract_snapshots = snapshot_repo
        self.contract_node_snapshots = node_snapshot_repo
        self.contract_node_value_snapshots = value_snapshot_repo


def _make_nodes(organization_id, contract_id, snapshot_date):
    root = make_contract_node(
        organization_id=organization_id,
        contract_id=contract_id,
        code="ROOT",
        budget=None,
        parent_id=None,
    )
    root.progress_history = {}

    leaf_a = make_contract_node(
        organization_id=organization_id,
        contract_id=contract_id,
        code="A",
        budget=Decimal("100"),
        parent_id=root.id,
    )
    leaf_a.progress_history = {snapshot_date: Decimal("0.5")}

    leaf_b = make_contract_node(
        organization_id=organization_id,
        contract_id=contract_id,
        code="B",
        budget=Decimal("300"),
        parent_id=root.id,
    )
    leaf_b.progress_history = {snapshot_date: Decimal("1.0")}

    return root, leaf_a, leaf_b


def test_execute_returns_existing_snapshot_for_same_contract_and_date():
    existing = ContractSnapshotBuilder().build()

    snapshot_repo = MagicMock()
    snapshot_repo.get_by_contract_and_date.return_value = existing

    service = CreateContractSnapshotService(
    )
    uow = _FakeUow(
        contract_repo=MagicMock(),
        node_repo=MagicMock(),
        line_repo=MagicMock(),
        snapshot_repo=snapshot_repo,
        node_snapshot_repo=MagicMock(),
        value_snapshot_repo=MagicMock(),
    )

    snapshot, created = service.execute(
        action=CreateContractSnapshotCommand(
            organization_id=uuid4(),
            actor_user_id=uuid4(),
            contract_id=uuid4(),
            snapshot_date=date(2026, 2, 12),
        ),
        uow=uow,
    )

    assert snapshot == existing
    assert created is False


def test_execute_raises_when_contract_is_missing():
    snapshot_repo = MagicMock()
    snapshot_repo.get_by_contract_and_date.return_value = None

    contract_repo = MagicMock()
    contract_repo.get.return_value = None

    service = CreateContractSnapshotService(
    )
    uow = _FakeUow(
        contract_repo=contract_repo,
        node_repo=MagicMock(),
        line_repo=MagicMock(),
        snapshot_repo=snapshot_repo,
        node_snapshot_repo=MagicMock(),
        value_snapshot_repo=MagicMock(),
    )

    with pytest.raises(ValueError, match="not found"):
        service.execute(
            action=CreateContractSnapshotCommand(
                organization_id=uuid4(),
                actor_user_id=uuid4(),
                contract_id=uuid4(),
                snapshot_date=date(2026, 2, 12),
            ),
            uow=uow,
        )


def test_execute_builds_and_persists_aggregated_snapshot():
    organization_id = uuid4()
    actor_user_id = uuid4()
    contract_id = uuid4()
    snapshot_date = date(2026, 2, 12)

    contract = (
        ContractBuilder()
        .with_organization_id(organization_id)
        .with_id(contract_id)
        .build()
    )
    root, leaf_a, leaf_b = _make_nodes(organization_id, contract_id, snapshot_date)

    vt_id = uuid4()
    line_a = (
        FinancialRecordLineBuilder()
        .with_organization_id(organization_id)
        .with_contract_id(contract_id)
        .with_contract_node_id(leaf_a.id)
        .with_value_type_id(vt_id)
        .with_created_at(datetime(2026, 2, 10, 12, 0, 0))
        .with_amount(Amount(Decimal("100"), VatRate.VAT_23))
        .build()
    )
    line_b = (
        FinancialRecordLineBuilder()
        .with_organization_id(organization_id)
        .with_contract_id(contract_id)
        .with_contract_node_id(leaf_b.id)
        .with_value_type_id(vt_id)
        .with_created_at(datetime(2026, 2, 11, 12, 0, 0))
        .with_amount(Amount(Decimal("200"), VatRate.VAT_23))
        .build()
    )

    contract_repo = MagicMock()
    contract_repo.get.return_value = contract
    node_repo = MagicMock()
    node_repo.list_by_contract.return_value = [root, leaf_a, leaf_b]
    line_repo = MagicMock()
    line_repo.list_by_contract_until.return_value = [line_a, line_b]

    snapshot_repo = MagicMock()
    snapshot_repo.get_by_contract_and_date.return_value = None
    node_snapshot_repo = MagicMock()
    value_snapshot_repo = MagicMock()

    id_values = iter([uuid4() for _ in range(20)])
    service = CreateContractSnapshotService(
        id_generator=lambda: next(id_values),
        clock=lambda: datetime(2026, 2, 12, 10, 0, 0),
    )
    uow = _FakeUow(
        contract_repo=contract_repo,
        node_repo=node_repo,
        line_repo=line_repo,
        snapshot_repo=snapshot_repo,
        node_snapshot_repo=node_snapshot_repo,
        value_snapshot_repo=value_snapshot_repo,
    )

    snapshot, created = service.execute(
        action=CreateContractSnapshotCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            contract_id=contract_id,
            snapshot_date=snapshot_date,
        ),
        uow=uow,
    )

    assert created is True
    assert snapshot.contract_id == contract_id
    assert snapshot.snapshot_date == snapshot_date

    snapshot_repo.add.assert_called_once_with(snapshot)
    node_snapshot_repo.add_many.assert_called_once()
    value_snapshot_repo.add_many.assert_called_once()

    node_snapshots = node_snapshot_repo.add_many.call_args.args[0]
    value_snapshots = value_snapshot_repo.add_many.call_args.args[0]

    assert len(node_snapshots) == 3
    by_contract_node_id = {ns.contract_node_id: ns for ns in node_snapshots}

    root_snapshot = by_contract_node_id[root.id]
    leaf_a_snapshot = by_contract_node_id[leaf_a.id]
    leaf_b_snapshot = by_contract_node_id[leaf_b.id]

    assert root_snapshot.planned_budget == Decimal("400")
    assert root_snapshot.progress == Decimal("0.875")
    assert leaf_a_snapshot.planned_budget == Decimal("100")
    assert leaf_a_snapshot.progress == Decimal("0.5")
    assert leaf_b_snapshot.planned_budget == Decimal("300")
    assert leaf_b_snapshot.progress == Decimal("1.0")

    assert len(value_snapshots) == 3
    by_node_snapshot_id = {v.node_snapshot_id: v for v in value_snapshots}

    root_values = by_node_snapshot_id[root_snapshot.id]
    assert root_values.net == Decimal("300")
    assert root_values.vat == Decimal("69.00")
    assert root_values.gross == Decimal("369.00")
    assert root_values.non_deductible == Decimal("0")
