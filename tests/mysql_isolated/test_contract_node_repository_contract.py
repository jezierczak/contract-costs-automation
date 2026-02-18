from datetime import date
from decimal import Decimal

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractStatus
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.contract_node_progress import ContractNodeProgress
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from contract_costs.repository.mysql.contract_repository import MySQLContractRepository
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder


def _make_node(*, org_id, contract_id, code="N1", parent_id=None):
    return ContractNode(
        id=new_uuid(),
        organization_id=org_id,
        created_at=utc_now(),
        created_by_user_id=new_uuid(),
        updated_at=None,
        updated_by_user_id=None,
        contract_id=contract_id,
        code=code,
        name=f"Node {code}",
        parent_id=parent_id,
        quantity=None,
        unit=None,
        budget=Decimal("100"),
        is_active=True,
        progress_history={},
    )


def _seed_contract_for_mysql(contract_node_repo_contract, org_id, contract_id):
    if not contract_node_repo_contract.__class__.__name__.startswith("MySQL"):
        return
    conn = contract_node_repo_contract._connection
    company_repo = MySQLCompanyRepository(connection=conn)
    contract_repo = MySQLContractRepository(connection=conn)
    owner = (
        CompanyBuilder()
        .with_id(new_uuid())
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_tax_number("8100000001")
        .build()
    )
    company_repo.add(owner)
    contract = (
        ContractBuilder()
        .with_id(contract_id)
        .with_organization_id(org_id)
        .with_owner(owner)
        .with_status(ContractStatus.ACTIVE)
        .with_code("CN-MYSQL-1")
        .build()
    )
    contract_repo.add(contract)


def test_contract_node_add_and_get(contract_node_repo_contract):
    org_id = new_uuid()
    contract_id = new_uuid()
    _seed_contract_for_mysql(contract_node_repo_contract, org_id, contract_id)
    node = _make_node(org_id=org_id, contract_id=contract_id)

    contract_node_repo_contract.add(node)

    loaded = contract_node_repo_contract.get(organization_id=org_id, contract_node_id=node.id)
    assert loaded is not None
    assert loaded.id == node.id
    assert loaded.code == node.code


def test_contract_node_get_isolated_by_org(contract_node_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    contract_id = new_uuid()
    _seed_contract_for_mysql(contract_node_repo_contract, org_a, contract_id)
    node = _make_node(org_id=org_a, contract_id=contract_id)
    contract_node_repo_contract.add(node)

    assert contract_node_repo_contract.get(organization_id=org_b, contract_node_id=node.id) is None


def test_contract_node_add_progress(contract_node_repo_contract):
    org_id = new_uuid()
    contract_id = new_uuid()
    _seed_contract_for_mysql(contract_node_repo_contract, org_id, contract_id)
    node = _make_node(org_id=org_id, contract_id=contract_id)
    contract_node_repo_contract.add(node)

    progress = ContractNodeProgress(
        id=new_uuid(),
        organization_id=org_id,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        contract_node_id=node.id,
        progress_date=date(2026, 2, 1),
        progress=Decimal("0.5"),
    )
    contract_node_repo_contract.add_progress(progress)

    loaded = contract_node_repo_contract.get(organization_id=org_id, contract_node_id=node.id)
    assert loaded is not None
    assert loaded.progress == Decimal("0.5")


def test_contract_node_list_by_parent(contract_node_repo_contract):
    org_id = new_uuid()
    contract_id = new_uuid()
    _seed_contract_for_mysql(contract_node_repo_contract, org_id, contract_id)
    parent = _make_node(org_id=org_id, contract_id=contract_id, code="P")
    child = _make_node(org_id=org_id, contract_id=contract_id, code="C", parent_id=parent.id)
    contract_node_repo_contract.add_all([parent, child])

    listed = contract_node_repo_contract.list_by_parent(organization_id=org_id, parent_id=parent.id)
    assert [n.id for n in listed] == [child.id]


def test_contract_node_delete_by_contract(contract_node_repo_contract):
    org_id = new_uuid()
    contract_id = new_uuid()
    _seed_contract_for_mysql(contract_node_repo_contract, org_id, contract_id)
    node = _make_node(org_id=org_id, contract_id=contract_id)
    contract_node_repo_contract.add(node)

    contract_node_repo_contract.delete_by_contract(organization_id=org_id, contract_id=contract_id)
    assert not contract_node_repo_contract.exists(organization_id=org_id, contract_node_id=node.id)
