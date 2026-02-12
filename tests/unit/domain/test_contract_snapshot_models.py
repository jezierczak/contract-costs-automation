
import pytest
from decimal import Decimal
from contract_costs.common.ids import new_uuid
from contract_costs.model.snapshot.contract_node_snapshot import ContractNodeSnapshot
from contract_costs.model.snapshot.contract_node_value_snapshot import ContractNodeValueSnapshot
from datetime import date
from contract_costs.common.time import utc_now
from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot




def test_contract_node_snapshot_creation():
    snapshot = ContractNodeSnapshot(
        id=new_uuid(),
        snapshot_id=new_uuid(),
        contract_node_id=new_uuid(),
        planned_budget=Decimal("1000"),
        progress=Decimal("0.75"),
    )

    assert snapshot.planned_budget == Decimal("1000")
    assert snapshot.progress == Decimal("0.75")



def test_contract_node_snapshot_disallows_dynamic_attributes():
    snapshot = ContractNodeSnapshot(
        id=new_uuid(),
        snapshot_id=new_uuid(),
        contract_node_id=new_uuid(),
        planned_budget=Decimal("1000"),
        progress=Decimal("0.75"),
    )

    with pytest.raises(AttributeError):
        snapshot.random = 123


def test_contract_node_value_snapshot_creation():
    snapshot = ContractNodeValueSnapshot(
        id=new_uuid(),
        node_snapshot_id=new_uuid(),
        value_type_id=new_uuid(),
        net=Decimal("100"),
        vat=Decimal("23"),
        gross=Decimal("123"),
        non_deductible=Decimal("0"),
    )

    assert snapshot.gross == Decimal("123")

def test_contract_node_value_snapshot_disallows_dynamic_attributes():
    snapshot = ContractNodeValueSnapshot(
        id=new_uuid(),
        node_snapshot_id=new_uuid(),
        value_type_id=new_uuid(),
        net=Decimal("100"),
        vat=Decimal("23"),
        gross=Decimal("123"),
        non_deductible=Decimal("0"),
    )

    with pytest.raises(AttributeError):
        snapshot.random = 123



def test_contract_snapshot_creation():
    snapshot = ContractSnapshot(
        id=new_uuid(),
        organization_id=new_uuid(),
        created_at=utc_now(),
        created_by_user_id=None,
        # updated_at=None,
        # updated_by_user_id=None,
        contract_id=new_uuid(),
        snapshot_date=date(2024, 1, 1),
    )

    assert snapshot.snapshot_date.year == 2024
