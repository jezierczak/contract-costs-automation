from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now

from contract_costs.model.value_type import ValueType
from contract_costs.model.value_direction import ValueDirection


def build_value_type():
    return ValueType(
        id=new_uuid(),
        organization_id=new_uuid(),
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        code="MATERIAL",
        name="Material",
        description=None,
        direction=ValueDirection.COST,
    )

def test_value_type_creation():
    vt = build_value_type()

    assert vt.code == "MATERIAL"
    assert vt.direction == ValueDirection.COST
    assert vt.is_active is True

def test_value_type_is_mutable():
    vt = build_value_type()

    vt.name = "Updated Name"

    assert vt.name == "Updated Name"

import pytest

def test_value_type_disallows_dynamic_attributes():
    vt = build_value_type()

    with pytest.raises(AttributeError):
        vt.random = 123
