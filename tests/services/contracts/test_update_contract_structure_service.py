from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from contract_costs.builders.cost_node_tree_builder import DefaultCostNodeTreeBuilder
from contract_costs.model.company import Company, CompanyType
from contract_costs.model.contract import Contract, ContractStarter, ContractStatus
from contract_costs.model.cost_node import CostNode
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository
from contract_costs.services.contracts.update_contract_structure_service import (
    UpdateContractStructureService,
)
from contract_costs.services.contracts.validators.cost_node_tree_validator import (
    CostNodeEntityValidator,
)

# ---------------------------------------------------------------------
# FIXTURES – DOMAIN
# ---------------------------------------------------------------------

@pytest.fixture
def owner_company() -> Company:
    return Company(
        id=uuid4(),
        name="Owner",
        tax_number="1111111111",
        description=None,
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.OWN,
        tags=set(),
        is_active=True,
    )


@pytest.fixture
def client_company() -> Company:
    return Company(
        id=uuid4(),
        name="Client",
        tax_number="2222222222",
        description=None,
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.CLIENT,
        tags=set(),
        is_active=True,
    )


@pytest.fixture
def contract_starter_1(owner_company, client_company) -> ContractStarter:
    return {
        "name": "Contract A",
        "code": "C-A",
        "contract_owner": owner_company,
        "client": client_company,
        "description": "Initial description",
        "start_date": date(2024, 1, 1),
        "end_date": None,
        "budget": Decimal("100000"),
        "path": Path("/contracts/C-A"),
        "status": ContractStatus.ACTIVE,
    }


@pytest.fixture
def contract_1(contract_starter_1) -> Contract:
    return Contract.from_contract_starter(contract_starter_1)


# ---------------------------------------------------------------------
# FIXTURES – COST NODE INPUT
# ---------------------------------------------------------------------

@pytest.fixture
def cost_node_tree_input():
    return [
        {
            "code": "ROOT",
            "name": "Root",
            "budget": Decimal("100000"),
            "quantity": None,
            "unit": None,
            "is_active": True,
            "children": [
                {
                    "code": "CH1",
                    "name": "Child 1",
                    "budget": Decimal("50000"),
                    "quantity": Decimal("10"),
                    "unit": UnitOfMeasure.PIECE,
                    "is_active": True,
                    "children": [],
                }
            ],
        }
    ]


# ---------------------------------------------------------------------
# FIXTURES – REPOS & SERVICE
# ---------------------------------------------------------------------

@pytest.fixture
def contract_repo():
    return InMemoryContractRepository()


@pytest.fixture
def cost_node_repo():
    return InMemoryCostNodeRepository()


@pytest.fixture
def update_contract_structure_service(contract_repo, cost_node_repo):
    return UpdateContractStructureService(
        contract_repository=contract_repo,
        cost_node_repository=cost_node_repo,
        cost_node_tree_builder=DefaultCostNodeTreeBuilder(),
        cost_node_tree_validator=CostNodeEntityValidator(),
    )


# ---------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------

def test_update_contract_structure_contract_not_found(
    update_contract_structure_service,
    contract_starter_1,
    cost_node_tree_input,
):
    with pytest.raises(ValueError, match="Contract does not exist"):
        update_contract_structure_service.execute(
            contract_id=uuid4(),
            contract_starter=contract_starter_1,
            cost_node_input=cost_node_tree_input,
        )


def test_update_contract_structure_hard_replace_when_no_costs(
    update_contract_structure_service,
    contract_repo,
    cost_node_repo,
    contract_1,
    contract_starter_1,
    cost_node_tree_input,
):
    contract_repo.add(contract_1)

    update_contract_structure_service.execute(
        contract_id=contract_1.id,
        contract_starter=contract_starter_1,
        cost_node_input=cost_node_tree_input,
    )

    nodes = cost_node_repo.list_by_contract(contract_1.id)
    assert len(nodes) == 2
    assert {n.code for n in nodes} == {"ROOT", "CH1"}


def test_update_contract_structure_safe_replace_updates_existing_node(
    update_contract_structure_service,
    contract_repo,
    cost_node_repo,
    contract_1,
monkeypatch):
    contract_repo.add(contract_1)

    root = CostNode(
        id=uuid4(),
        contract_id=contract_1.id,
        code="ROOT",
        name="Old Root",
        parent_id=None,
        quantity=None,
        unit=None,
        budget=Decimal("100000"),
        is_active=True,
    )
    cost_node_repo.add(root)

    # symulacja: node ma już koszty
    monkeypatch.setattr(cost_node_repo, "has_costs", lambda _cid: True)
    monkeypatch.setattr(cost_node_repo, "node_has_costs", lambda _nid: True)

    update_contract_structure_service.execute(
        contract_id=contract_1.id,
        contract_starter={
            **contract_1.__dict__,
            "name": "Updated Contract",
        },
        cost_node_input=[
            {
                "code": "ROOT",
                "name": "Updated Root",
                "budget": Decimal("100000"),
                "quantity": None,
                "unit": None,
                "is_active": True,
                "children": [],
            }
        ],
    )

    nodes = cost_node_repo.list_by_contract(contract_1.id)
    assert len(nodes) == 1
    assert nodes[0].id == root.id
    assert nodes[0].name == "Updated Root"


def test_update_contract_structure_rejects_empty_cost_node_input(
    update_contract_structure_service,
    contract_repo,
    contract_1,
):
    contract_repo.add(contract_1)

    with pytest.raises(ValueError, match="At least one cost node root is required"):
        update_contract_structure_service.execute(
            contract_id=contract_1.id,
            contract_starter=contract_1.__dict__,
            cost_node_input=[],
        )

