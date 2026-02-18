from contract_costs.common.ids import new_uuid
from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractType
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder


def _ensure_owner_for_mysql(contract_repo_contract, owner):
    if contract_repo_contract.__class__.__name__.startswith("MySQL"):
        company_repo = MySQLCompanyRepository(connection=contract_repo_contract._connection)
        company_repo.add(owner)


def test_contract_add_and_get(contract_repo_contract):
    org_id = new_uuid()
    owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_tax_number("8000000001")
        .build()
    )
    _ensure_owner_for_mysql(contract_repo_contract, owner)

    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(owner)
        .with_code("C-ADD-1")
        .build()
    )
    contract_repo_contract.add(contract)

    loaded = contract_repo_contract.get(organization_id=org_id, contract_id=contract.id)
    assert loaded is not None
    assert loaded.id == contract.id
    assert loaded.organization_id == contract.organization_id
    assert loaded.code == contract.code
    assert loaded.name == contract.name
    assert loaded.owner.id == owner.id


def test_contract_get_isolated_by_org(contract_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    owner = (
        CompanyBuilder()
        .with_organization_id(org_a)
        .with_role(CompanyType.OWN)
        .with_tax_number("8000000002")
        .build()
    )
    _ensure_owner_for_mysql(contract_repo_contract, owner)
    contract = (
        ContractBuilder()
        .with_organization_id(org_a)
        .with_owner(owner)
        .with_code("C-ISO-1")
        .build()
    )
    contract_repo_contract.add(contract)

    assert contract_repo_contract.get(organization_id=org_b, contract_id=contract.id) is None


def test_contract_get_by_code(contract_repo_contract):
    org_id = new_uuid()
    owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_tax_number("8000000003")
        .build()
    )
    _ensure_owner_for_mysql(contract_repo_contract, owner)
    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(owner)
        .with_code("C-CODE-1")
        .build()
    )
    contract_repo_contract.add(contract)

    loaded = contract_repo_contract.get_by_code(org_id, "C-CODE-1")
    assert loaded is not None
    assert loaded.id == contract.id


def test_contract_update(contract_repo_contract):
    org_id = new_uuid()
    owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_tax_number("8000000004")
        .build()
    )
    _ensure_owner_for_mysql(contract_repo_contract, owner)
    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(owner)
        .with_code("C-UPD-1")
        .build()
    )
    contract_repo_contract.add(contract)

    contract.name = "Updated Contract Name"
    contract_repo_contract.update(contract)

    loaded = contract_repo_contract.get(organization_id=org_id, contract_id=contract.id)
    assert loaded is not None
    assert loaded.name == "Updated Contract Name"


def test_contract_list_by_type(contract_repo_contract):
    org_id = new_uuid()
    owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_tax_number("8000000005")
        .build()
    )
    _ensure_owner_for_mysql(contract_repo_contract, owner)
    project = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(owner)
        .with_code("C-PROJ-1")
        .with_contract_type(ContractType.PROJECT)
        .build()
    )
    system = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(owner)
        .with_code("C-SYS-1")
        .with_contract_type(ContractType.SYSTEM)
        .build()
    )
    system.contract_type = ContractType.SYSTEM
    contract_repo_contract.add(project)
    contract_repo_contract.add(system)

    listed = contract_repo_contract.list_contracts(org_id, contract_type=ContractType.PROJECT)
    assert [c.id for c in listed] == [project.id]
