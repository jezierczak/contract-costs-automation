from datetime import date
from decimal import Decimal
from uuid import uuid4

from contract_costs.services.snapshots.dto.contract_snapshot_details_dto import (
    ContractSnapshotDetailsDTO,
)
from contract_costs.services.snapshots.dto.contract_snapshot_node_dto import (
    ContractSnapshotNodeDTO,
)
from contract_costs.services.snapshots.dto.contract_snapshot_value_row_dto import (
    ContractSnapshotValueRowDTO,
)


def test_contract_snapshot_node_dto_holds_values() -> None:
    node = ContractSnapshotNodeDTO(
        node_id=uuid4(),
        parent_id=None,
        code="N-1",
        name="Node 1",
        planned_budget=Decimal("1000"),
        progress=Decimal("0.5"),
        net_cost=Decimal("100"),
        gross_cost=Decimal("123"),
        revenue=Decimal("0"),
        non_deductible=Decimal("10"),
        is_leaf=True,
    )
    assert node.code == "N-1"
    assert node.is_leaf is True


def test_contract_snapshot_details_dto_holds_nodes() -> None:
    node = ContractSnapshotNodeDTO(
        node_id=uuid4(),
        parent_id=None,
        code="N-1",
        name="Node 1",
        planned_budget=Decimal("1000"),
        progress=Decimal("0.5"),
        net_cost=Decimal("100"),
        gross_cost=Decimal("123"),
        revenue=Decimal("0"),
        non_deductible=Decimal("10"),
        is_leaf=True,
    )
    details = ContractSnapshotDetailsDTO(
        snapshot_id=uuid4(),
        snapshot_date=date(2026, 2, 17),
        contract_code="C-1",
        nodes=[node],
    )
    assert details.contract_code == "C-1"
    assert len(details.nodes) == 1


def test_contract_snapshot_value_row_dto_holds_financial_values() -> None:
    row = ContractSnapshotValueRowDTO(
        snapshot_id=uuid4(),
        snapshot_date=date(2026, 2, 17),
        contract_id=uuid4(),
        node_id=uuid4(),
        value_type_code="VT-1",
        direction="cost",
        net=Decimal("10"),
        vat=Decimal("2.3"),
        gross=Decimal("12.3"),
        non_deductible=Decimal("0"),
    )
    assert row.value_type_code == "VT-1"
    assert row.gross == Decimal("12.3")

