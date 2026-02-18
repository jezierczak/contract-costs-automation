from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.snapshots.contract_snapshot_query_service import (
    ContractSnapshotQueryService,
)
from contract_costs.services.snapshots.dto.contract_snapshot_query import (
    GetContractSnapshotQuery,
    ListContractSnapshotsQuery,
)
from tests.builders.contract_builder import ContractBuilder
from tests.builders.contract_node_snapshot_builder import ContractNodeSnapshotBuilder
from tests.builders.contract_node_value_snapshot_builder import (
    ContractNodeValueSnapshotBuilder,
)
from tests.builders.contract_snapshot_builder import ContractSnapshotBuilder
from tests.builders.value_type_builder import ValueTypeBuilder
from tests.helpers.contracts_helpers import make_contract_node


def test_list_snapshots_aggregates_cost_and_revenue_for_root():
    organization_id = uuid4()
    contract = ContractBuilder().with_organization_id(organization_id).build()
    snapshot = (
        ContractSnapshotBuilder()
        .with_organization_id(organization_id)
        .with_contract_id(contract.id)
        .with_snapshot_date(date(2026, 2, 12))
        .build()
    )
    root_node_snapshot = (
        ContractNodeSnapshotBuilder()
        .with_snapshot_id(snapshot.id)
        .build()
    )

    cost_type = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_direction(ValueDirection.COST)
        .build()
    )
    revenue_type = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_direction(ValueDirection.REVENUE)
        .build()
    )

    cost_value = (
        ContractNodeValueSnapshotBuilder()
        .with_node_snapshot_id(root_node_snapshot.id)
        .build()
    )
    cost_value = type(cost_value)(
        id=cost_value.id,
        node_snapshot_id=cost_value.node_snapshot_id,
        value_type_id=cost_type.id,
        net=Decimal("100"),
        vat=Decimal("23"),
        gross=Decimal("123"),
        non_deductible=Decimal("10"),
    )
    revenue_value = (
        ContractNodeValueSnapshotBuilder()
        .with_node_snapshot_id(root_node_snapshot.id)
        .build()
    )
    revenue_value = type(revenue_value)(
        id=revenue_value.id,
        node_snapshot_id=revenue_value.node_snapshot_id,
        value_type_id=revenue_type.id,
        net=Decimal("200"),
        vat=Decimal("46"),
        gross=Decimal("246"),
        non_deductible=Decimal("5"),
    )

    uow = SimpleNamespace(
        contracts=MagicMock(get=MagicMock(return_value=contract)),
        contract_nodes=MagicMock(),
        value_types=MagicMock(list_all=MagicMock(return_value=[cost_type, revenue_type])),
        contract_snapshots=MagicMock(list_all=MagicMock(return_value=[snapshot])),
        contract_node_snapshots=MagicMock(get_root_by_snapshot=MagicMock(return_value=root_node_snapshot)),
        contract_node_value_snapshots=MagicMock(
            list_by_node_snapshot=MagicMock(return_value=[cost_value, revenue_value])
        ),
    )
    service = ContractSnapshotQueryService()

    result = service.execute(
        action=ListContractSnapshotsQuery(
            organization_id=organization_id,
            actor_user_id=uuid4(),
            contract_id=None,
        ),
        uow=uow,
    )

    assert len(result) == 1
    dto = result[0]
    assert dto.contract_code == contract.code
    assert dto.net_cost == Decimal("100")
    assert dto.gross_cost == Decimal("123")
    assert dto.non_deductible == Decimal("10")
    assert dto.revenue == Decimal("200")


def test_get_snapshot_returns_nodes_with_cost_and_revenue_values():
    organization_id = uuid4()
    contract = ContractBuilder().with_organization_id(organization_id).with_code("C-77").build()
    snapshot = (
        ContractSnapshotBuilder()
        .with_organization_id(organization_id)
        .with_contract_id(contract.id)
        .with_snapshot_date(date(2026, 2, 12))
        .build()
    )

    root = make_contract_node(
        organization_id=organization_id,
        contract_id=contract.id,
        code="ROOT",
        budget=None,
        parent_id=None,
    )
    leaf = make_contract_node(
        organization_id=organization_id,
        contract_id=contract.id,
        code="A",
        budget=Decimal("100"),
        parent_id=root.id,
    )

    root_ns = (
        ContractNodeSnapshotBuilder()
        .with_snapshot_id(snapshot.id)
        .build()
    )
    root_ns = type(root_ns)(
        id=root_ns.id,
        snapshot_id=root_ns.snapshot_id,
        contract_node_id=root.id,
        planned_budget=Decimal("100"),
        progress=Decimal("0.5"),
    )

    leaf_ns = (
        ContractNodeSnapshotBuilder()
        .with_snapshot_id(snapshot.id)
        .build()
    )
    leaf_ns = type(leaf_ns)(
        id=leaf_ns.id,
        snapshot_id=leaf_ns.snapshot_id,
        contract_node_id=leaf.id,
        planned_budget=Decimal("100"),
        progress=Decimal("0.5"),
    )

    cost_type = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_direction(ValueDirection.COST)
        .build()
    )
    revenue_type = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_direction(ValueDirection.REVENUE)
        .build()
    )

    cost_value = SimpleNamespace(
        node_snapshot_id=leaf_ns.id,
        value_type_code=cost_type.id,
        net=Decimal("100"),
        vat=Decimal("23"),
        gross=Decimal("123"),
        non_deductible=Decimal("7"),
    )
    revenue_value = SimpleNamespace(
        node_snapshot_id=leaf_ns.id,
        value_type_code=revenue_type.id,
        net=Decimal("50"),
        vat=Decimal("11.5"),
        gross=Decimal("61.5"),
        non_deductible=Decimal("2"),
    )

    uow = SimpleNamespace(
        contracts=MagicMock(get=MagicMock(return_value=contract)),
        contract_nodes=MagicMock(list_by_contract=MagicMock(return_value=[root, leaf])),
        value_types=MagicMock(list_all=MagicMock(return_value=[cost_type, revenue_type])),
        contract_snapshots=MagicMock(list_all=MagicMock(return_value=[snapshot])),
        contract_node_snapshots=MagicMock(list_by_snapshot=MagicMock(return_value=[root_ns, leaf_ns])),
        contract_node_value_snapshots=MagicMock(list_by_snapshot=MagicMock(return_value=[cost_value, revenue_value])),
    )
    service = ContractSnapshotQueryService()

    dto = service.execute(
        action=GetContractSnapshotQuery(
            organization_id=organization_id,
            actor_user_id=uuid4(),
            snapshot_id_prefix=str(snapshot.id),
        ),
        uow=uow,
    )

    assert dto.contract_code == "C-77"
    assert len(dto.nodes) == 2
    by_code = {n.code: n for n in dto.nodes}
    leaf_dto = by_code["A"]
    assert leaf_dto.net == Decimal("100")
    assert leaf_dto.vat == Decimal("23")
    assert leaf_dto.gross == Decimal("123")
    assert leaf_dto.non_deductible == Decimal("7")
    assert leaf_dto.revenue == Decimal("50")
    assert leaf_dto.revenue_non_deductible == Decimal("2")


class _SnapshotRepoStub:
    def __init__(self, snapshots):
        self._snapshots = snapshots

    def list_all(self, organization_id):
        return self._snapshots


def test_resolve_snapshot_raises_when_prefix_is_ambiguous():
    common_prefix = "12345678"
    snap1 = type("S", (), {"id": UUID("12345678-0000-0000-0000-000000000001")})()
    snap2 = type("S", (), {"id": UUID("12345678-0000-0000-0000-000000000002")})()

    with pytest.raises(ValueError, match="ambiguous"):
        ContractSnapshotQueryService.resolve_snapshot(
            organization_id=uuid4(),
            prefix=common_prefix,
            repo=_SnapshotRepoStub([snap1, snap2]),
        )


def test_resolve_snapshot_raises_when_no_match():
    with pytest.raises(ValueError, match="No snapshot found"):
        ContractSnapshotQueryService.resolve_snapshot(
            organization_id=uuid4(),
            prefix="deadbeef",
            repo=_SnapshotRepoStub([]),
        )
