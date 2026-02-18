from contract_costs.common.ids import new_uuid
from tests.builders.value_type_builder import ValueTypeBuilder


def _assert_same_value_type(actual, expected):
    assert actual is not None
    assert actual.id == expected.id
    assert actual.organization_id == expected.organization_id
    assert actual.code == expected.code
    assert actual.name == expected.name
    assert actual.description == expected.description
    assert actual.direction == expected.direction
    assert actual.is_active == expected.is_active


def test_value_type_add_and_get(value_type_repo_contract):
    org_id = new_uuid()
    vt = ValueTypeBuilder().with_organization_id(org_id).build()
    value_type_repo_contract.add(vt)

    loaded = value_type_repo_contract.get(
        organization_id=org_id,
        value_type_id=vt.id,
    )
    _assert_same_value_type(loaded, vt)


def test_value_type_get_isolated_by_org(value_type_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    vt = ValueTypeBuilder().with_organization_id(org_a).build()
    value_type_repo_contract.add(vt)

    loaded = value_type_repo_contract.get(
        organization_id=org_b,
        value_type_id=vt.id,
    )
    assert loaded is None


def test_value_type_get_by_code(value_type_repo_contract):
    org_id = new_uuid()
    vt = ValueTypeBuilder().with_organization_id(org_id).with_code("LAB").build()
    value_type_repo_contract.add(vt)

    loaded = value_type_repo_contract.get_by_code(org_id, "LAB")
    _assert_same_value_type(loaded, vt)


def test_value_type_list_active_only(value_type_repo_contract):
    org_id = new_uuid()
    active = ValueTypeBuilder().with_organization_id(org_id).with_code("A").with_is_active(True).build()
    inactive = ValueTypeBuilder().with_organization_id(org_id).with_code("B").with_is_active(False).build()
    value_type_repo_contract.add(active)
    value_type_repo_contract.add(inactive)

    listed = value_type_repo_contract.list_active(organization_id=org_id)
    assert [v.id for v in listed] == [active.id]


def test_value_type_update_persists_changes(value_type_repo_contract):
    org_id = new_uuid()
    vt = ValueTypeBuilder().with_organization_id(org_id).with_code("OLD").build()
    value_type_repo_contract.add(vt)

    vt.name = "Updated Name"
    value_type_repo_contract.update(vt)

    loaded = value_type_repo_contract.get(organization_id=org_id, value_type_id=vt.id)
    assert loaded is not None
    assert loaded.name == "Updated Name"


def test_value_type_list_all_and_exists(value_type_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    vt_a = ValueTypeBuilder().with_organization_id(org_a).with_code("A1").build()
    vt_b = ValueTypeBuilder().with_organization_id(org_b).with_code("B1").build()
    value_type_repo_contract.add(vt_a)
    value_type_repo_contract.add(vt_b)

    assert [v.id for v in value_type_repo_contract.list_all(organization_id=org_a)] == [vt_a.id]
    assert value_type_repo_contract.exists(organization_id=org_a, value_type_id=vt_a.id) is True
    assert value_type_repo_contract.exists(organization_id=org_b, value_type_id=vt_a.id) is False
