import pytest
from contract_costs.common.ids import new_uuid
from contract_costs.model.company import CompanyType
from tests.builders.company_builder import CompanyBuilder


def test_add_and_get_company(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .build()
    )

    company_repo.add(company)

    result = company_repo.get(company.id, org_id)

    assert result == company


def test_get_is_isolated_by_organization(company_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org1)
        .build()
    )

    company_repo.add(company)

    assert company_repo.get(company.id, org2) is None



def test_update_existing_company(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .build()
    )

    company_repo.add(company)

    company.name = "Updated"
    company_repo.update(company)

    assert company_repo.get(company.id, org_id).name == "Updated"




def test_update_non_existing_raises(company_repo):
    org_id = new_uuid()

    with pytest.raises(KeyError):
        company_repo.update(CompanyBuilder()
        .with_organization_id(org_id)
        .build())


def test_delete_removes_company(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .build()
    )
    company_repo.add(company)

    company_repo.delete(company.id, org_id)

    assert company_repo.get(company.id, org_id) is None


def test_list_all_filters_by_org(company_repo):

    org1 = new_uuid()
    org2 = new_uuid()

    c1 = (
        CompanyBuilder()
        .with_organization_id(org1)
        .build()
    )
    c2 = (
        CompanyBuilder()
        .with_organization_id(org2)
        .build()
    )

    company_repo.add(c1)
    company_repo.add(c2)

    result = company_repo.list_all(org1)

    assert result == [c1]


def test_get_by_tax_number(company_repo):

    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("999")
        .build()
    )


    company_repo.add(company)

    result = company_repo.get_by_tax_number("999", org_id)

    assert result == company


def test_get_owners_returns_only_active_own(company_repo):
    org_id = new_uuid()

    owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_is_active(True)
        .build()
    )

    supplier = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .build()
    )

    company_repo.add(owner)
    company_repo.add(supplier)

    result = company_repo.get_owners(org_id)

    assert result == [owner]


def test_find_by_email(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_email("test@example.com")
        .build()
    )

    company_repo.add(company)

    result = company_repo.find_by_email(org_id, "test@example.com")

    assert result == [company]



def test_find_by_name_like_case_insensitive(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("Super Company")
        .build()
    )

    company_repo.add(company)

    result = company_repo.find_by_name_like(org_id, "super")

    assert result == [company]



def test_find_by_street_tokens(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_street("Krakowska 10")
        .build()
    )

    company_repo.add(company)

    result = company_repo.find_by_street_tokens(org_id, ["krak"])

    assert result == [company]
