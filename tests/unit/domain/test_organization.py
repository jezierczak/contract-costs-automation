
import pytest


from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now

from contract_costs.model.identity.organization import Organization


def build_org(settings=None):
    return Organization(
        id=new_uuid(),
        code="REMONTIVO",
        name="Remontivo Sp. z o.o.",
        is_active=True,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        settings=settings,
    )

def test_organization_creation():
    org = build_org()

    assert org.code == "REMONTIVO"
    assert org.is_active is True

def test_organization_is_immutable():
    org = build_org()

    with pytest.raises(Exception):
        org.name = "New Name"


def test_settings_dict_is_mutable_even_if_class_is_frozen():
    org = build_org(settings={"a": 1})

    org.settings["b"] = 2

    assert org.settings["b"] == 2


def test_organizations_with_same_data_are_equal():
    now = utc_now()
    org_id = new_uuid()

    org1 = Organization(
        id=org_id,
        code="X",
        name="Name",
        is_active=True,
        created_at=now,
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
    )

    org2 = Organization(
        id=org_id,
        code="X",
        name="Name",
        is_active=True,
        created_at=now,
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
    )

    assert org1 == org2
