from contract_costs.common.ids import new_uuid
from tests.builders.value_type_builder import ValueTypeBuilder


def test_add_and_get(value_type_repo):
    org_id = new_uuid()

    vt = (
        ValueTypeBuilder()
        .with_organization_id(org_id)
        .build()
    )

    value_type_repo.add(vt)

    result = value_type_repo.get(
        organization_id=org_id,
        value_type_id=vt.id,
    )

    assert result == vt

def test_get_isolated_by_org(value_type_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    vt = (
        ValueTypeBuilder()
        .with_organization_id(org1)
        .build()
    )

    value_type_repo.add(vt)

    assert value_type_repo.get(
        organization_id=org2,
        value_type_id=vt.id,
    ) is None

def test_get_by_code(value_type_repo):
    org_id = new_uuid()

    vt = (
        ValueTypeBuilder()
        .with_organization_id(org_id)
        .with_code("SALARY")
        .build()
    )

    value_type_repo.add(vt)

    result = value_type_repo.get_by_code(org_id, "SALARY")

    assert result == vt

def test_list_all_filters_by_org(value_type_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    vt1 = ValueTypeBuilder().with_organization_id(org1).build()
    vt2 = ValueTypeBuilder().with_organization_id(org2).build()

    value_type_repo.add(vt1)
    value_type_repo.add(vt2)

    result = value_type_repo.list_all(organization_id=org1)

    assert result == [vt1]

def test_list_active_returns_only_active(value_type_repo):
    org_id = new_uuid()

    active = (
        ValueTypeBuilder()
        .with_organization_id(org_id)
        .with_is_active(True)
        .build()
    )

    inactive = (
        ValueTypeBuilder()
        .with_organization_id(org_id)
        .with_is_active(False)
        .build()
    )

    value_type_repo.add(active)
    value_type_repo.add(inactive)

    result = value_type_repo.list_active(organization_id=org_id)

    assert result == [active]

def test_exists(value_type_repo):
    org_id = new_uuid()

    vt = (
        ValueTypeBuilder()
        .with_organization_id(org_id)
        .build()
    )

    value_type_repo.add(vt)

    assert value_type_repo.exists(
        organization_id=org_id,
        value_type_id=vt.id,
    ) is True

def test_update(value_type_repo):
    org_id = new_uuid()

    vt = (
        ValueTypeBuilder()
        .with_organization_id(org_id)
        .with_code("OLD")
        .build()
    )

    value_type_repo.add(vt)

    vt.code = "NEW"
    value_type_repo.update(vt)

    updated = value_type_repo.get(
        organization_id=org_id,
        value_type_id=vt.id,
    )

    assert updated.code == "NEW"
