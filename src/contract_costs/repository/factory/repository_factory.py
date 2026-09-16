from contract_costs.repository.company_dashboard.company_dashboard_repository import CompanyDashboardRepository
from contract_costs.repository.company_ksef_settings_repository import CompanyKsefSettingsRepository
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.repository.identity.organization_repository import OrganizationRepository
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.repository.inmemory.company_dashboard.company_dashboard_repository import \
    InMemoryCompanyDashboardRepository
from contract_costs.repository.inmemory.company_ksef_settings_repository import InMemoryCompanyKsefSettingsRepository
from contract_costs.repository.inmemory.document_repository import InMemoryDocumentRepository
from contract_costs.repository.inmemory.identity.organization_repository import InMemoryOrganizationRepository
from contract_costs.repository.inmemory.identity.organization_user_repository import InMemoryOrganizationUserRepository
from contract_costs.repository.inmemory.identity.user_repository import InMemoryUserRepository
from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.repository.financial_record_payment_repository import FinancialRecordPaymentRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.inmemory.number_sequence_repository import InMemoryNumberSequenceRepository
from contract_costs.repository.inmemory.session_repository import InMemorySessionRepository
from contract_costs.repository.mysql.company_dashboard.company_dashboard_repository import \
    MySQLCompanyDashboardRepository
from contract_costs.repository.mysql.company_ksef_settings_repository import MySQLCompanyKsefSettingsRepository
from contract_costs.repository.mysql.document_repository import MySQLDocumentRepository
from contract_costs.repository.mysql.identity.organization_repository import MySqlOrganizationRepository
from contract_costs.repository.mysql.identity.organization_user_repository import MySqlOrganizationUserRepository
from contract_costs.repository.mysql.identity.user_repository import MySqlUserRepository
from contract_costs.repository.mysql.number_sequence_repository import MySQLNumberSequenceRepository
from contract_costs.repository.mysql.session_repository import MySQLSessionRepository
from contract_costs.repository.number_sequence_repository import NumberSequenceRepository
from contract_costs.repository.session_repository import SessionRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.repository.snapshot.contract_node_snapshot_repository import ContractNodeSnapshotRepository
from contract_costs.repository.snapshot.contract_node_value_snapshot_repository import \
    ContractNodeValueSnapshotRepository
from contract_costs.repository.snapshot.contract_snapshot_repository import ContractSnapshotRepository
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from contract_costs.unit_of_work.mysql_unit_of_work import MySQLUnitOfWork
from contract_costs.unit_of_work.unit_of_work import UnitOfWork



# mysql
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from contract_costs.repository.mysql.financial_record_repository import MySQLFinancialRecordRepository
from contract_costs.repository.mysql.financial_record_line_repository import MySQLFinancialRecordLineRepository
from contract_costs.repository.mysql.financial_record_payment_repository import MySQLFinancialRecordPaymentRepository
from contract_costs.repository.mysql.contract_repository import MySQLContractRepository
from contract_costs.repository.mysql.contract_node_repository import MySQLContractNodeRepository
from contract_costs.repository.mysql.value_type_repository import MySQLValueTypeRepository
from contract_costs.repository.mysql.snapshot.contract_snapshot_repository import MySQLContractSnapshotRepository
from contract_costs.repository.mysql.snapshot.contract_node_snapshot_repository import \
    MySQLContractNodeSnapshotRepository
from contract_costs.repository.mysql.snapshot.contract_node_value_snapshot_repository import \
    MySQLContractNodeValueSnapshotRepository

# in-memory
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.repository.inmemory.financial_record_repository import InMemoryFinancialRecordRepository
from contract_costs.repository.inmemory.financial_record_line_repository import InMemoryFinancialRecordLineRepository
from contract_costs.repository.inmemory.financial_record_payment_repository import (
    InMemoryFinancialRecordPaymentRepository,
)
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.contract_node_repository import InMemoryContractNodeRepository
from contract_costs.repository.inmemory.value_type_repository import InMemoryValueTypeRepository
from contract_costs.repository.inmemory.snapshot.contract_snapshot_repository import InMemoryContractSnapshotRepository
from contract_costs.repository.inmemory.snapshot.contract_node_snapshot_repository import \
    InMemoryContractNodeSnapshotRepository
from contract_costs.repository.inmemory.snapshot.contract_node_value_snapshot_repository import \
    InMemoryContractNodeValueSnapshotRepository

from enum import Enum


class RepoBackend(str, Enum):
    MYSQL = "mysql"
    MEMORY = "memory"


class RepositoryFactory:
    def __init__(self, backend: RepoBackend) -> None:
        self.backend = backend

    def company_repository(self) -> CompanyRepository:
        return (
            MySQLCompanyRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryCompanyRepository()
        )

    def company_ksef_settings_repository(self) -> CompanyKsefSettingsRepository:
        return (
            MySQLCompanyKsefSettingsRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryCompanyKsefSettingsRepository()
        )

    def invoice_repository(self) -> FinancialRecordRepository:
        return (
            MySQLFinancialRecordRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryFinancialRecordRepository()
        )

    def invoice_line_repository(self) -> FinancialRecordLineRepository:
        return (
            MySQLFinancialRecordLineRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryFinancialRecordLineRepository()
        )

    def financial_record_payment_repository(self) -> FinancialRecordPaymentRepository:
        return (
            MySQLFinancialRecordPaymentRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryFinancialRecordPaymentRepository()
        )

    def contract_repository(self) -> ContractRepository:
        return (
            MySQLContractRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryContractRepository()
        )

    def contract_node_repository(self) -> ContractNodeRepository:
        return (
            MySQLContractNodeRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryContractNodeRepository()
        )

    def value_type_repository(self) -> ValueTypeRepository:
        return (
            MySQLValueTypeRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryValueTypeRepository()
        )

    def contract_snapshot_repository(self) -> ContractSnapshotRepository:
        return (
            MySQLContractSnapshotRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryContractSnapshotRepository()
        )

    def contract_node_snapshot_repository(self) -> ContractNodeSnapshotRepository:
        return (
            MySQLContractNodeSnapshotRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryContractNodeSnapshotRepository()
        )

    def contract_node_value_snapshot_repository(self) -> ContractNodeValueSnapshotRepository:
        return(
            MySQLContractNodeValueSnapshotRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryContractNodeValueSnapshotRepository()
        )

    def organization_repository(self) -> OrganizationRepository:
        return (
            MySqlOrganizationRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryOrganizationRepository()
        )

    def organization_user_repository(self) -> OrganizationUserRepository:
        return (
            MySqlOrganizationUserRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryOrganizationUserRepository()
        )

    def user_repository(self) -> UserRepository:
        return (
            MySqlUserRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryUserRepository()
        )

    def document_repository(self) -> DocumentRepository:
        return (
            MySQLDocumentRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryDocumentRepository()
        )

    def number_sequence_repository(self) -> NumberSequenceRepository:
        return (
            MySQLNumberSequenceRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryNumberSequenceRepository()
        )

    def session_repository(self) -> SessionRepository:
        return (
            MySQLSessionRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemorySessionRepository()
                )

    def unit_of_work(self) -> UnitOfWork:
        return (
            MySQLUnitOfWork()
            if self.backend == RepoBackend.MYSQL
            else InMemoryUnitOfWork()
        )

    def company_dashboard_repository(self) -> CompanyDashboardRepository:
        return (
            MySQLCompanyDashboardRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryCompanyDashboardRepository()
        )
