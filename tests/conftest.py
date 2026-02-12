import pytest
from contract_costs.cli.context import get_services
from contract_costs.repository.factory.repository_factory import RepoBackend
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.repository.inmemory.contract_node_repository import InMemoryContractNodeRepository
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.document_repository import InMemoryDocumentRepository
from contract_costs.repository.inmemory.financial_record_line_repository import InMemoryFinancialRecordLineRepository
from contract_costs.repository.inmemory.financial_record_repository import InMemoryFinancialRecordRepository
from contract_costs.repository.inmemory.identity.in_memory_storage_repository import InMemoryIdentityStorage
from contract_costs.repository.inmemory.identity.organization_repository import InMemoryOrganizationRepository
from contract_costs.repository.inmemory.identity.organization_user_repository import InMemoryOrganizationUserRepository
from contract_costs.repository.inmemory.identity.user_repository import InMemoryUserRepository
from contract_costs.repository.inmemory.number_sequence_repository import InMemoryNumberSequenceRepository
from contract_costs.repository.inmemory.snapshot.contract_node_snapshot_repository import \
    InMemoryContractNodeSnapshotRepository
from contract_costs.repository.inmemory.snapshot.contract_node_value_snapshot_repository import \
    InMemoryContractNodeValueSnapshotRepository
from contract_costs.repository.inmemory.snapshot.contract_snapshot_repository import InMemoryContractSnapshotRepository
from contract_costs.repository.inmemory.value_type_repository import InMemoryValueTypeRepository
from contract_costs.services.catalogues.record_file_organizer import RecordFileOrganizer
from contract_costs.services.catalogues.record_file_workworkflow_service import RecordFileWorkflowService
from contract_costs.services.companies.activate_company_service import ActivateCompanyService
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.companies.deactivate_company_service import DeactivateCompanyService
from contract_costs.services.companies.update_company_service import UpdateCompanyService
from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.user_builder import UserBuilder


@pytest.fixture
def services_memory():
    """
    Świeży kontener serwisów na każdy test.
    """
    return get_services(RepoBackend.MEMORY)


@pytest.fixture
def action_bus(services_memory):
    return services_memory.action_bus


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
def company_repo():
    return InMemoryCompanyRepository()

@pytest.fixture
def contract_node_repo():
    return InMemoryContractNodeRepository()


@pytest.fixture
def contract_repo():
    return InMemoryContractRepository()

@pytest.fixture
def document_repo():
    return InMemoryDocumentRepository()

@pytest.fixture
def line_repo():
    return InMemoryFinancialRecordLineRepository()


@pytest.fixture
def financial_record_repo():
    return InMemoryFinancialRecordRepository()


@pytest.fixture
def number_sequence_repo():
    return InMemoryNumberSequenceRepository()

@pytest.fixture
def value_type_repo():
    return InMemoryValueTypeRepository()

@pytest.fixture
def contract_node_snapshot_repo():
    return InMemoryContractNodeSnapshotRepository()

@pytest.fixture
def contract_node_value_snapshot_repo():
    return InMemoryContractNodeValueSnapshotRepository()

@pytest.fixture
def contract_snapshot_repo():
    return InMemoryContractSnapshotRepository()

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
    company_repo = InMemoryCompanyRepository()
    document_repo = InMemoryDocumentRepository()
    organizer = RecordFileOrganizer()

    service = RecordFileWorkflowService(
        company_repository=company_repo,
        file_organizer=organizer,
        document_repository=document_repo,
    )

    return service, company_repo, document_repo


@pytest.fixture
def create_service(company_repo):
    return CreateCompanyService(company_repo)


@pytest.fixture
def update_service(company_repo):
    return UpdateCompanyService(company_repo)


@pytest.fixture
def activate_service(company_repo):
    return ActivateCompanyService(company_repo)


@pytest.fixture
def deactivate_service(company_repo):
    return DeactivateCompanyService(company_repo)