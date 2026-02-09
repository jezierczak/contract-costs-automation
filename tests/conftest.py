from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from contract_costs.builders.contract_node_tree_builder import DefaultContractNodeTreeBuilder
from contract_costs.model.amount import VatRate, Amount
from contract_costs.model.company import Company, Address, BankAccount, CompanyType, Contact
from contract_costs.model.contract import ContractStatus, Contract
from datetime import date, datetime

from contract_costs.model.contract_node import ContractNodeInput, ContractNode
from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.contract_node_repository import InMemoryContractNodeRepository
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.contracts.validators.contract_node_tree_validator import ContractNodeEntityValidator


NOW= datetime.now()
TEST_ORG_ID = uuid4()
TEST_USER_ID = uuid4()

@pytest.fixture
def create_contract_service():
    return CreateContractService(
        contract_repository=InMemoryContractRepository(),
        contract_node_repository=InMemoryContractNodeRepository(),
        contract_node_tree_builder=DefaultContractNodeTreeBuilder(),
        contract_node_tree_validator=ContractNodeEntityValidator()
    )

@pytest.fixture
def contract_owner() -> Company:
    return Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="Contract Owner",
        description="Description Owner",
        tax_number="2222222222",

        address=Address(
            street="Street Owner",
            city="City Owner",
            zip_code="34-700",
            country="Country_owner",
        ),
        contact=Contact(
            phone_number="+44 555 555 555",
            email="example@example.com",
        ),
        bank_account=BankAccount(
            account_number="91221122112211221122221111",
            country_code="PL",
        ),

        role=CompanyType.OWN,
        tags={"important"},
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

@pytest.fixture
def contract_company() -> Company:
    return Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="Contract Company",
        description="Description",
        tax_number="1112223334",

        address=Address(
            street="Street",
            city="City",
            zip_code="40-310",
            country="Country",
        ),
        contact=Contact(
            phone_number="+44 555 555 555",
            email="email@aa.com",
        ),
        bank_account=BankAccount(
            account_number="1122112211221122112222111122",
            country_code=None,  # jeżeli brak – jawnie None
        ),

        role=CompanyType.COOPERATIVE,
        tags={"important", "friendly"},
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )



# @pytest.fixture
# def contract_starter_1(contract_owner: Company,contract_company: Company) -> ContractStarter:
#     return {    "name": "Contract Starter 1",
#                 "code": "CONTRACT_STARTER1",
#                 "contract_owner": contract_owner,
#                 "client": contract_company,
#                 "description": "Description",
#
#                 "start_date": date(2026, 1, 1),
#                 "end_date": date (2026, 12, 31),
#
#                 "budget": Decimal("100000"),
#                 "path": Path("./path/company1"),
#                 "status": ContractStatus.PLANNED
#
#     }
#
# @pytest.fixture
# def contract_1(contract_starter_1) -> Contract:
#     return Contract.from_contract_starter(contract_starter_1)

# @pytest.fixture
# def contract_1(
#     create_contract_service: CreateContractService,
#     contract_owner: Company,
#     contract_company: Company,
# ) -> Contract:
#
#     contract_id = uuid4()
#
#     contract = Contract(
#         id=contract_id,
#         organization_id=TEST_ORG_ID,
#         code="CONTRACT_STARTER1",
#         name="Contract Starter 1",
#         owner=contract_owner,
#         client=contract_company,
#         description="Description",
#         start_date=date(2026, 1, 1),
#         end_date=date(2026, 12, 31),
#         budget=Decimal("100000"),
#         path=Path("./path/company1"),
#         status=ContractStatus.PLANNED,
#         created_at=NOW,
#         created_by_user_id=TEST_USER_ID,
#         updated_at=None,
#         updated_by_user_id=None,
#     )
#
#     create_contract_service.execute(
#         organization_id=TEST_ORG_ID,
#         actor_user_id=TEST_USER_ID,
#         contract=contract,
#         nodes=[],  # albo drzewo, jeśli test tego wymaga
#     )
#
#     return contract


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
def cost_node_tree_1() -> ContractNodeInput:
    return {
        "code":"WYB",
        "name":"wyburzenia",
        "quantity": Decimal("1"),
        "unit": None,
        "budget":Decimal("100000"),
        "is_active":True,
        "children": [
            { "code":"WYB_SCI",
            "name":"wyburzenia scian",
              "quantity": Decimal("10"),
              "unit": UnitOfMeasure.CUBIC_METER,
            "budget":Decimal("50000"),
              "is_active": True,
            "children": []
            },
            {"code": "WYB_POS",
             "name": "wyburzenia posadzki",
             "quantity": Decimal("100"),
             "unit": UnitOfMeasure.SQUARE_METER,
             "budget": Decimal("50000"),
             "is_active": True,
             "children": []
             }
        ]
    }

@pytest.fixture
def invoice_line_1(contract_1) -> FinancialRecordLine:
    return FinancialRecordLine(
        id = uuid4(),
        invoice_id= uuid4(),
        contract_id= contract_1.id,
        contract_node_id= uuid4(),
        value_type_id= uuid4(),
        quantity= Decimal(2),
        unit = UnitOfMeasure.TON,
        amount = Amount(Decimal("10000"),VatRate.VAT_23),
        description = "Description1",
        item_name="Item1"
    )

@pytest.fixture
def invoice_line_2(contract_2) -> FinancialRecordLine:
    return FinancialRecordLine(
        id=uuid4(),
        invoice_id=uuid4(),
        contract_id=contract_2.id,
        contract_node_id=uuid4(),
        value_type_id=uuid4(),
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
    return ContractNode(
        id=uuid4(),
        contract_id=node_contract_id,
        parent_id=None,
        code="ROOT",
        name="Root",
        budget=Decimal("1000"),
        is_active=True,
        quantity= Decimal("1"),
        unit=None,
        progress_history={}
    )


@pytest.fixture
def child_node(node_contract_id, root_node):
    return ContractNode(
        id=uuid4(),
        contract_id=node_contract_id,
        parent_id=root_node.id,
        code="CHILD",
        name="Child",
        budget=Decimal("500"),
        is_active=True,
        quantity=Decimal("10"),
        unit=UnitOfMeasure.METER,
        progress_history={}
    )
