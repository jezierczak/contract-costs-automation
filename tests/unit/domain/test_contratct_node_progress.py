from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now

from datetime import date
from decimal import Decimal

from contract_costs.model.contract_node_progress import ContractNodeProgress


def build_progress(
    *,
    progress_value=Decimal("0.5"),
    progress_date=date(2024, 1, 1),
):
    return ContractNodeProgress(
        id=new_uuid(),
        organization_id=new_uuid(),
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        contract_node_id=new_uuid(),
        progress_date=progress_date,
        progress=progress_value,
    )


def test_contract_node_progress_creation():
    progress = ContractNodeProgress(
        id=new_uuid(),
        organization_id=new_uuid(),
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        contract_node_id=new_uuid(),
        progress_date=date(2024, 1, 1),
        progress=Decimal("0.5"),
    )

    assert progress.progress == Decimal("0.5")

import pytest

def test_contract_node_progress_disallows_dynamic_attributes():
    progress = build_progress()

    with pytest.raises(AttributeError):
        progress.random = 123

def test_contract_node_progress_is_mutable():
    progress = build_progress()

    progress.progress = Decimal("0.8")

    assert progress.progress == Decimal("0.8")
