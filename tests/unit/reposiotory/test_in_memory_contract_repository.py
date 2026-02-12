from contract_costs.common.ids import new_uuid
from tests.builders.contract_builder import ContractBuilder


def test_add_and_get_contract(contract_repo):
    org_id = new_uuid()

    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .build()
    )

    contract_repo.add(contract)

    result = contract_repo.get(org_id, contract.id)

    assert result == contract

def test_get_isolated_by_organization(contract_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    contract = (
        ContractBuilder()
        .with_organization_id(org1)
        .build()
    )

    contract_repo.add(contract)

    assert contract_repo.get(org2, contract.id) is None


def test_list_filters_by_organization(contract_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    c1 = ContractBuilder().with_organization_id(org1).build()
    c2 = ContractBuilder().with_organization_id(org2).build()

    contract_repo.add(c1)
    contract_repo.add(c2)

    result = contract_repo.list_contracts(org1)

    assert result == [c1]

def test_update_overwrites_existing(contract_repo):
    org_id = new_uuid()

    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .build()
    )

    contract_repo.add(contract)

    contract.name = "Updated"
    contract_repo.update(contract)

    result = contract_repo.get(org_id, contract.id)

    assert result.name == "Updated"


def test_exists_returns_true(contract_repo):
    org_id = new_uuid()

    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .build()
    )

    contract_repo.add(contract)

    assert contract_repo.exists(org_id, contract.id) is True

def test_exists_false_for_wrong_org(contract_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    contract = (
        ContractBuilder()
        .with_organization_id(org1)
        .build()
    )

    contract_repo.add(contract)

    assert contract_repo.exists(org2, contract.id) is False


def test_get_by_code(contract_repo):
    org_id = new_uuid()

    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_code("C-123")
        .build()
    )

    contract_repo.add(contract)

    result = contract_repo.get_by_code(org_id, "C-123")

    assert result == contract
