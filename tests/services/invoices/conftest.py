from pathlib import Path
from decimal import Decimal
from datetime import date
from uuid import uuid4

import pytest

# ============================================================
# MODELE DOMENOWE
# ============================================================

from contract_costs.model.company import Company, CompanyType
from contract_costs.model.contract import (
    Contract,
    ContractStatus,
    ContractStarter,
)
from contract_costs.model.cost_node import CostNode
from contract_costs.model.cost_type import CostType
from contract_costs.model.unit_of_measure import UnitOfMeasure

# ============================================================
# REPOZYTORIA (IN-MEMORY)
# ============================================================

from contract_costs.repository.inmemory.contract_repository import (
    InMemoryContractRepository,
)
from contract_costs.repository.inmemory.cost_node_repository import (
    InMemoryCostNodeRepository,
)
from contract_costs.repository.inmemory.cost_type_repository import (
    InMemoryCostTypeRepository,
)
from contract_costs.repository.inmemory.invoice_line_repository import (
    InMemoryInvoiceLineRepository,
)
from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository

# ============================================================
# SERWISY
# ============================================================

from contract_costs.services.invoices.invoice_line_update_service import (
    InvoiceLineUpdateService,
)
from contract_costs.services.invoices.invoice_update_service import InvoiceUpdateService
from contract_costs.services.invoices.ochestrator.invoice_ingest_orchestrator import InvoiceIngestOrchestrator


# ============================================================
# REPO FIXTURES
# ============================================================

@pytest.fixture
def invoice_line_repo():
    return InMemoryInvoiceLineRepository()

@pytest.fixture
def invoice_repo():
    return InMemoryInvoiceRepository()


# ============================================================
# COMPANY FIXTURES
# ============================================================

@pytest.fixture
def owner_company() -> Company:
    return Company(
        id=uuid4(),
        name="Owner Sp. z o.o.",
        tax_number="1111111111",
        description="Owner contract description",
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
        name="Client Sp. z o.o.",
        tax_number="2222222222",
        description="Client contract description",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.CLIENT,  # 👈 ważne rozróżnienie domenowe
        tags=set(),
        is_active=True,
    )


# ============================================================
# CONTRACT FIXTURES
# ============================================================

@pytest.fixture
def contract_1(owner_company, client_company) -> Contract:
    starter: ContractStarter = {
        "name": "Test Contract",
        "code": "C1",
        "contract_owner": owner_company,
        "client": client_company,
        "description": "Test contract description",
        "start_date": date(2024, 1, 1),
        "end_date": None,
        "budget": Decimal("100000"),
        "path": Path("/contracts/C1"),
        "status": ContractStatus.ACTIVE,
    }
    return Contract.from_contract_starter(starter)


@pytest.fixture
def contract_repo(contract_1):
    repo = InMemoryContractRepository()
    repo.add(contract_1)
    return repo


# ============================================================
# COST NODE FIXTURES
# ============================================================

@pytest.fixture
def cost_node_root(contract_1):
    return CostNode(
        id=uuid4(),
        contract_id=contract_1.id,
        code="N1",
        name="Root Node",
        parent_id=None,
        quantity=None,
        unit=None,
        budget=Decimal("100000"),
        is_active=True,
    )


@pytest.fixture
def cost_node_child(cost_node_root, contract_1):
    return CostNode(
        id=uuid4(),
        contract_id=contract_1.id,
        code="N1.1",
        name="Child Node",
        parent_id=cost_node_root.id,
        quantity=Decimal("10"),
        unit=UnitOfMeasure.PIECE,
        budget=Decimal("50000"),
        is_active=True,
    )


@pytest.fixture
def inactive_cost_node(contract_1):
    return CostNode(
        id=uuid4(),
        contract_id=contract_1.id,
        code="N2",
        name="Inactive Node",
        parent_id=None,
        quantity=None,
        unit=None,
        budget=None,
        is_active=False,
    )


@pytest.fixture
def cost_node_repo(cost_node_root, cost_node_child, inactive_cost_node):
    repo = InMemoryCostNodeRepository()
    repo.add(cost_node_root)
    repo.add(cost_node_child)
    repo.add(inactive_cost_node)
    return repo


# ============================================================
# COST NODE INPUT (DO BUILDERÓW / IMPORTERÓW)
# UWAGA: NIE używać bezpośrednio z repozytoriami
# ============================================================

@pytest.fixture
def cost_node_input_tree():
    return {
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
            },
            {
                "code": "CH2",
                "name": "Child 2",
                "budget": None,
                "quantity": None,
                "unit": None,
                "is_active": False,
                "children": [],
            },
        ],
    }


# ============================================================
# COST TYPE FIXTURES
# ============================================================

@pytest.fixture
def cost_type_material() -> CostType:
    return CostType(
        id=uuid4(),
        code="MATERIAL",
        name="Materiały",
        description="Koszty materiałów budowlanych",
        is_active=True,
    )


@pytest.fixture
def cost_type_salary() -> CostType:
    return CostType(
        id=uuid4(),
        code="SALARY",
        name="Wynagrodzenia",
        description="Koszty pracy",
        is_active=True,
    )


@pytest.fixture
def inactive_cost_type() -> CostType:
    return CostType(
        id=uuid4(),
        code="ARCHIVED",
        name="Archiwalny",
        description=None,
        is_active=False,
    )


@pytest.fixture
def cost_type_repo(
    cost_type_material,
    cost_type_salary,
    inactive_cost_type,
):
    repo = InMemoryCostTypeRepository()
    repo.add(cost_type_material)
    repo.add(cost_type_salary)
    repo.add(inactive_cost_type)
    return repo


# ============================================================
# SERVICE FIXTURE
# ============================================================

@pytest.fixture
def invoice_line_update_service(
    invoice_line_repo,
    contract_repo,
    cost_node_repo,
    cost_type_repo,
):
    return InvoiceLineUpdateService(
        invoice_line_repository=invoice_line_repo,
        contract_repository=contract_repo,
        cost_node_repository=cost_node_repo,
        cost_type_repository=cost_type_repo,
    )


@pytest.fixture
def invoice_update_service(invoice_repo):
    return InvoiceUpdateService(invoice_repo)


# @pytest.fixture
# def invoice_line_update_service(
#     invoice_line_repo,
#     contract_repo,
#     cost_node_repo,
#     cost_type_repo,
# ):
#     return InvoiceLineUpdateService(
#         invoice_line_repo,
#         contract_repo,
#         cost_node_repo,
#         cost_type_repo,
#     )


@pytest.fixture
def orchestrator(invoice_update_service, invoice_line_update_service):
    return InvoiceIngestOrchestrator(
        invoice_service=invoice_update_service,
        invoice_line_service=invoice_line_update_service,
    )

