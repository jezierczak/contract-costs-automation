import pytest
from contract_costs.cli.context import get_services
from contract_costs.repository.inmemory.identity.in_memory_storage_repository import InMemoryIdentityStorage
from contract_costs.repository.inmemory.identity.organization_repository import InMemoryOrganizationRepository
from contract_costs.repository.inmemory.identity.organization_user_repository import InMemoryOrganizationUserRepository
from contract_costs.repository.inmemory.identity.user_repository import InMemoryUserRepository

from contract_costs.services.catalogues.record_file_organizer import RecordFileOrganizer
from contract_costs.services.catalogues.record_file_workworkflow_service import RecordFileWorkflowService
from contract_costs.services.companies.activate_company_service import ActivateCompanyService
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.companies.deactivate_company_service import DeactivateCompanyService
from contract_costs.services.companies.update_company_service import UpdateCompanyService
from contract_costs.services.contracts.builders.contract_node_tree_builder import \
    DefaultContractNodeTreeBuilder
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.contracts.system_contract.create_system_contract_orchestrator import \
    CreateSystemContractOrchestrator
from contract_costs.services.contracts.validators.contract_node_tree_validator import ContractNodeEntityValidator
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.user_builder import UserBuilder


@pytest.fixture
def services_memory():
    """
    Świeży kontener serwisów na każdy test.
    """
    return get_services("memory")


@pytest.fixture
def action_bus(services_memory):
    return services_memory.action_bus


@pytest.fixture
def uow_test(services_memory):
    return services_memory.uow


@pytest.fixture
def uow():
    return InMemoryUnitOfWork()

# @pytest.fixture
# def contract_repo(services_memory):
#     return services_memory.contract_repository


@pytest.fixture
def user():
    return UserBuilder().build()


@pytest.fixture
def organization():
    return OrganizationBuilder().build()

#REPOS
@pytest.fixture
def company_repo(uow):
    return uow.companies

@pytest.fixture
def contract_node_repo(uow):
    return uow.contract_nodes


@pytest.fixture
def contract_repo(uow):
    return uow.contracts

@pytest.fixture
def document_repo(uow):
    return uow.documents

@pytest.fixture
def line_repo(uow):
    return uow.financial_record_lines


@pytest.fixture
def financial_record_repo(uow):
    return uow.financial_records


@pytest.fixture
def financial_record_payment_repo(uow):
    return uow.financial_record_payments


@pytest.fixture
def number_sequence_repo(uow):
    return uow.number_sequences

@pytest.fixture
def value_type_repo(uow):
    return uow.value_types

@pytest.fixture
def contract_node_snapshot_repo(uow):
    return uow.contract_node_snapshots

@pytest.fixture
def contract_node_value_snapshot_repo(uow):
    return uow.contract_node_value_snapshots

@pytest.fixture
def contract_snapshot_repo(uow):
    return uow.contract_snapshots

@pytest.fixture
def identity_storage():
    return InMemoryIdentityStorage()

@pytest.fixture
def organization_repo(identity_storage):
    return InMemoryOrganizationRepository(identity_storage)

@pytest.fixture
def user_repo(identity_storage):
    return InMemoryUserRepository(identity_storage)

@pytest.fixture
def organization_user_repo(identity_storage):
    return InMemoryOrganizationUserRepository(identity_storage)


@pytest.fixture
def workflow_service():
    organizer = RecordFileOrganizer()
    return RecordFileWorkflowService(file_organizer=organizer)

@pytest.fixture
def create_contract():
    return CreateContractService(
        contract_node_tree_builder=DefaultContractNodeTreeBuilder(),
        contract_node_tree_validator=ContractNodeEntityValidator()
    )


@pytest.fixture
def create_system_contract(create_contract):
    return CreateSystemContractOrchestrator(
        create_contract_service=create_contract
    )

@pytest.fixture
def create_company_service(create_system_contract):
    return CreateCompanyService(create_system_contract=create_system_contract)


@pytest.fixture
def update_service(company_repo):
    return UpdateCompanyService()


@pytest.fixture
def activate_service(company_repo):
    return ActivateCompanyService()


@pytest.fixture
def deactivate_service(company_repo):
    return DeactivateCompanyService()


def pytest_addoption(parser):
    parser.addoption(
        "--run-mysql-isolated",
        action="store_true",
        default=False,
        help="Run isolated MySQL Testcontainers tests.",
    )
    parser.addoption(
        "--run-mysql-contract",
        action="store_true",
        default=False,
        help="Deprecated alias for --run-mysql-isolated.",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "mysql_isolated: isolated repository tests against MySQL Testcontainers",
    )


def pytest_collection_modifyitems(config, items):
    run_mysql_isolated = config.getoption("--run-mysql-isolated") or config.getoption(
        "--run-mysql-contract"
    )

    for item in items:
        path_str = str(item.fspath).replace("\\", "/")
        if "/tests/mysql_isolated/" in path_str or path_str.endswith("/tests/mysql_isolated"):
            item.add_marker(pytest.mark.mysql_isolated)

    if run_mysql_isolated:
        return
    skip_mysql_isolated = pytest.mark.skip(
        reason="mysql_isolated tests are disabled by default. Use --run-mysql-isolated."
    )
    for item in items:
        if "mysql_isolated" in item.keywords:
            item.add_marker(skip_mysql_isolated)
