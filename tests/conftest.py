from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from contract_costs.builders.cost_node_tree_builder import DefaultCostNodeTreeBuilder
from contract_costs.model.amount import VatRate, Amount
from contract_costs.model.company import Company, Address, BankAccount, CompanyType, CompanyTag
from contract_costs.model.contract import ContractStarter, ContractStatus, Contract
from datetime import date

from contract_costs.model.cost_node import CostNodeInput, CostNode
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository
from contract_costs.services.contracts.create_contract_service import CreateContractService


@pytest.fixture
def create_contract_service():
    return CreateContractService(
        contract_repository=InMemoryContractRepository(),
        cost_node_repository=InMemoryCostNodeRepository(),
        cost_node_tree_builder=DefaultCostNodeTreeBuilder(),
    )

@pytest.fixture
def contract_owner() -> Company:
    return Company(
    id = uuid4(),
    name =  "Contract Owner",
    description = "Description Owner",
    tax_number =  "2222222222",
    address = Address(
        street = "Street Owner",
        city =  "City Owner",
        zip_code = "34-700",
        country = "Country_owner"
    ),
    bank_account = BankAccount("91221122112211221122221111","PL"),
    role = CompanyType.OWN,
    tags ={"important"},
    is_active = True
    )

@pytest.fixture
def contract_company() -> Company:
    return Company(
    id = uuid4(),
    name =  "Contract Company",
    description = "Description",
    tax_number =  "1112223334",
    address = Address(
        street = "Street",
        city =  "City",
        zip_code = "40-310",
        country = "Country"
    ),
    bank_account = BankAccount("1122112211221122112222111122"),
    role = CompanyType.COOPERATIVE,
    tags ={"important","friendly"},
    is_active = True
    )


@pytest.fixture
def contract_starter_1(contract_owner: Company,contract_company: Company) -> ContractStarter:
    return {    "name": "Contract Starter 1",
                "code": "CONTRACT_STARTER1",
                "contract_owner": contract_owner,
                "client": contract_company,
                "description": "Description",

                "start_date": date(2026, 1, 1),
                "end_date": date (2026, 12, 31),

                "budget": Decimal("100000"),
                "path": Path("./path/company1"),
                "status": ContractStatus.PLANNED

    }

@pytest.fixture
def contract_1(contract_starter_1) -> Contract:
    return Contract.from_contract_starter(contract_starter_1)

@pytest.fixture
def contract_2(contract_owner,contract_company) -> Contract:
    return Contract(
        id = uuid4(),
        code="CODE",
        name = "Contract 2",
        owner= contract_owner,
        client = contract_company,
        description= "Description Contract 2",

        start_date = date(2025, 1, 1),
        end_date= date(2025, 12, 1),

        budget = Decimal("200000"),
        path = Path("./path/contract2"),
        status= ContractStatus.COMPLETED
    )

@pytest.fixture
def cost_node_tree_1() -> CostNodeInput:
    return {
        "code":"WYB",
        "name":"wyburzenia",
        "quantity": Decimal("1"),
        "unit": None,
        "budget":Decimal("100000"),
        "children": [
            { "code":"WYB_SCI",
            "name":"wyburzenia scian",
              "quantity": Decimal("10"),
              "unit": UnitOfMeasure.CUBIC_METER,
            "budget":Decimal("50000"),
            "children": []
            },
            {"code": "WYB_POS",
             "name": "wyburzenia posadzki",
             "quantity": Decimal("100"),
             "unit": UnitOfMeasure.SQUARE_METER,
             "budget": Decimal("50000"),
             "children": []
             }
        ]
    }

@pytest.fixture
def invoice_line_1(contract_1) -> InvoiceLine:
    return InvoiceLine(
        id = uuid4(),
        invoice_id= uuid4(),
        contract_id= contract_1.id,
        cost_node_id= uuid4(),
        cost_type_id= uuid4(),
        quantity= Decimal(2),
        unit = UnitOfMeasure.TON,
        amount = Amount(Decimal("10000"),VatRate.VAT_23),
        description = "Description1",
        item_name="Item1"
    )

@pytest.fixture
def invoice_line_2(contract_2) -> InvoiceLine:
    return InvoiceLine(
        id=uuid4(),
        invoice_id=uuid4(),
        contract_id=contract_2.id,
        cost_node_id=uuid4(),
        cost_type_id=uuid4(),
        quantity=Decimal(1),
        unit=UnitOfMeasure.METER,
        amount=Amount(Decimal("5000"), VatRate.VAT_8),
        description="Description2",
        item_name="Item2"
    )

@pytest.fixture
def node_contract_id():
    return uuid4()

@pytest.fixture
def root_node(node_contract_id):
    return CostNode(
        id=uuid4(),
        contract_id=node_contract_id,
        parent_id=None,
        code="ROOT",
        name="Root",
        budget=Decimal("1000"),
        is_active=True,
        quantity= Decimal("1"),
        unit=None,
    )


@pytest.fixture
def child_node(node_contract_id, root_node):
    return CostNode(
        id=uuid4(),
        contract_id=node_contract_id,
        parent_id=root_node.id,
        code="CHILD",
        name="Child",
        budget=Decimal("500"),
        is_active=True,
        quantity=Decimal("10"),
        unit=UnitOfMeasure.METER,
    )
