from contract_costs.common.ids import new_uuid
from contract_costs.model.company import CompanyType
from tests.builders.company_builder import CompanyBuilder


def _assert_same_company(actual, expected):
    assert actual is not None
    assert actual.id == expected.id
    assert actual.organization_id == expected.organization_id
    assert actual.name == expected.name
    assert actual.tax_number == expected.tax_number
    assert actual.role == expected.role
    assert actual.is_active == expected.is_active


def test_company_add_and_get(company_repo_contract):
    org_id = new_uuid()
    company = CompanyBuilder().with_organization_id(org_id).build()

    company_repo_contract.add(company)

    loaded = company_repo_contract.get(company.id, org_id)
    _assert_same_company(loaded, company)


def test_company_get_is_organization_isolated(company_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    company = CompanyBuilder().with_organization_id(org_a).build()

    company_repo_contract.add(company)

    assert company_repo_contract.get(company.id, org_b) is None


def test_company_update_existing(company_repo_contract):
    org_id = new_uuid()
    company = CompanyBuilder().with_organization_id(org_id).build()
    company_repo_contract.add(company)

    company.name = "Updated Name"
    company_repo_contract.update(company)

    updated = company_repo_contract.get(company.id, org_id)
    _assert_same_company(updated, company)


def test_company_delete(company_repo_contract):
    org_id = new_uuid()
    company = CompanyBuilder().with_organization_id(org_id).build()
    company_repo_contract.add(company)

    company_repo_contract.delete(company.id, org_id)

    assert company_repo_contract.get(company.id, org_id) is None


def test_company_get_owners_returns_only_active_own(company_repo_contract):
    org_id = new_uuid()
    owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1000000001")
        .with_role(CompanyType.OWN)
        .with_is_active(True)
        .build()
    )
    supplier = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1000000002")
        .with_role(CompanyType.SUPPLIER)
        .with_is_active(True)
        .build()
    )
    inactive_owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1000000003")
        .with_role(CompanyType.OWN)
        .with_is_active(False)
        .build()
    )

    company_repo_contract.add(owner)
    company_repo_contract.add(supplier)
    company_repo_contract.add(inactive_owner)

    owners = company_repo_contract.get_owners(org_id)
    assert [o.id for o in owners] == [owner.id]


def test_company_list_all_exists_and_get_by_tax_number(company_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    company_a = (
        CompanyBuilder()
        .with_organization_id(org_a)
        .with_tax_number("2000000001")
        .build()
    )
    company_b = (
        CompanyBuilder()
        .with_organization_id(org_b)
        .with_tax_number("2000000002")
        .build()
    )
    company_repo_contract.add(company_a)
    company_repo_contract.add(company_b)

    listed = company_repo_contract.list_all(org_a)
    assert [c.id for c in listed] == [company_a.id]
    assert company_repo_contract.exists(company_a.id, org_a) is True
    assert company_repo_contract.exists(company_a.id, org_b) is False
    assert company_repo_contract.get_by_tax_number("2000000001", org_a).id == company_a.id
    assert company_repo_contract.get_by_tax_number("2000000001", org_b) is None


def test_company_exists_owner_and_finders(company_repo_contract):
    org_id = new_uuid()
    owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_tax_number("2000000010")
        .with_bank_account("65103011880000000059830200", "PL")
        .with_email("owner@example.com")
        .with_phone("123456789")
        .with_name("Owner Company")
        .with_street("Krakowska 10")
        .build()
    )
    supplier = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .with_tax_number("2000000011")
        .with_bank_account("11111111111111111111111111", "PL")
        .with_email("supplier@example.com")
        .with_phone("999999999")
        .with_name("Supplier Company")
        .with_street("Warszawska 20")
        .build()
    )
    company_repo_contract.add(owner)
    company_repo_contract.add(supplier)

    assert company_repo_contract.exists_owner(org_id) is True
    assert [c.id for c in company_repo_contract.find_by_bank_account(org_id, "65103011880000000059830200")] == [owner.id]
    assert [c.id for c in company_repo_contract.find_by_email(org_id, "owner@example.com")] == [owner.id]
    assert [c.id for c in company_repo_contract.find_by_phone(org_id, "123456789")] == [owner.id]
    assert [c.id for c in company_repo_contract.find_by_name_like(org_id, "Owner")] == [owner.id]
    assert [c.id for c in company_repo_contract.find_by_street_tokens(org_id, ["krak"])] == [owner.id]
    assert company_repo_contract.find_by_street_tokens(org_id, []) == []


def test_company_reference_numbering_mode_roundtrip(company_repo_contract):
    from dataclasses import replace

    from contract_costs.model.company import ReferenceNumberingMode

    org_id = new_uuid()
    company = CompanyBuilder().with_organization_id(org_id).build()
    company_repo_contract.add(company)

    loaded = company_repo_contract.get(company.id, org_id)
    assert loaded.reference_numbering_mode is None

    company_repo_contract.update(replace(loaded, reference_numbering_mode=ReferenceNumberingMode.MONTHLY))
    assert company_repo_contract.get(company.id, org_id).reference_numbering_mode == ReferenceNumberingMode.MONTHLY

    company_repo_contract.update(replace(loaded, reference_numbering_mode=None))
    assert company_repo_contract.get(company.id, org_id).reference_numbering_mode is None
