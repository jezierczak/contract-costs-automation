from contract_costs.repository.inmemory.business_event_repository import InMemoryBusinessEventRepository
from contract_costs.repository.inmemory.company_dashboard.company_dashboard_repository import \
    InMemoryCompanyDashboardRepository
from contract_costs.repository.inmemory.company_ksef_settings_repository import InMemoryCompanyKsefSettingsRepository
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.repository.inmemory.contract_node_repository import InMemoryContractNodeRepository
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.document_repository import InMemoryDocumentRepository
from contract_costs.repository.inmemory.financial_record_line_repository import InMemoryFinancialRecordLineRepository
from contract_costs.repository.inmemory.financial_record_payment_repository import (
    InMemoryFinancialRecordPaymentRepository,
)
from contract_costs.repository.inmemory.financial_record_repository import InMemoryFinancialRecordRepository
from contract_costs.repository.inmemory.identity.in_memory_storage_repository import InMemoryIdentityStorage
from contract_costs.repository.inmemory.identity.organization_repository import InMemoryOrganizationRepository
from contract_costs.repository.inmemory.identity.organization_user_repository import InMemoryOrganizationUserRepository
from contract_costs.repository.inmemory.identity.user_repository import InMemoryUserRepository
from contract_costs.repository.inmemory.number_sequence_repository import InMemoryNumberSequenceRepository
from contract_costs.repository.inmemory.session_repository import InMemorySessionRepository
from contract_costs.repository.inmemory.snapshot.contract_node_snapshot_repository import (
    InMemoryContractNodeSnapshotRepository,
)
from contract_costs.repository.inmemory.snapshot.contract_node_value_snapshot_repository import (
    InMemoryContractNodeValueSnapshotRepository,
)
from contract_costs.repository.inmemory.snapshot.contract_snapshot_repository import InMemoryContractSnapshotRepository
from contract_costs.repository.inmemory.value_type_repository import InMemoryValueTypeRepository
from contract_costs.repository.session_repository import SessionRepository
from contract_costs.unit_of_work.unit_of_work import UnitOfWork


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        super().__init__()
        identity_storage = InMemoryIdentityStorage()

        self._companies = InMemoryCompanyRepository()
        self._financial_record_lines = InMemoryFinancialRecordLineRepository()
        self._financial_records = InMemoryFinancialRecordRepository(
            line_repository=self._financial_record_lines,
        )
        self._financial_record_payments = InMemoryFinancialRecordPaymentRepository()
        self._contracts = InMemoryContractRepository()
        self._contract_nodes = InMemoryContractNodeRepository()
        self._value_types = InMemoryValueTypeRepository()
        self._contract_snapshots = InMemoryContractSnapshotRepository()
        self._contract_node_snapshots = InMemoryContractNodeSnapshotRepository()
        self._contract_node_value_snapshots = InMemoryContractNodeValueSnapshotRepository()
        self._organizations = InMemoryOrganizationRepository(identity_storage)
        self._organization_users = InMemoryOrganizationUserRepository(identity_storage)
        self._users = InMemoryUserRepository(identity_storage)
        self._documents = InMemoryDocumentRepository()
        self._number_sequences = InMemoryNumberSequenceRepository()
        self._business_events = InMemoryBusinessEventRepository()
        self._sessions =InMemorySessionRepository()
        self._company_dashboard = InMemoryCompanyDashboardRepository()
        self._company_ksef_settings = InMemoryCompanyKsefSettingsRepository()

    @property
    def companies(self):
        return self._companies

    @property
    def financial_records(self):
        return self._financial_records

    @property
    def financial_record_lines(self):
        return self._financial_record_lines

    @property
    def financial_record_payments(self):
        return self._financial_record_payments

    @property
    def contracts(self):
        return self._contracts

    @property
    def contract_nodes(self):
        return self._contract_nodes

    @property
    def value_types(self):
        return self._value_types

    @property
    def contract_snapshots(self):
        return self._contract_snapshots

    @property
    def contract_node_snapshots(self):
        return self._contract_node_snapshots

    @property
    def contract_node_value_snapshots(self):
        return self._contract_node_value_snapshots

    @property
    def organizations(self):
        return self._organizations

    @property
    def organization_users(self):
        return self._organization_users

    @property
    def users(self):
        return self._users

    @property
    def documents(self):
        return self._documents

    @property
    def number_sequences(self):
        return self._number_sequences
    @property
    def business_events(self):
        return self._business_events

    @property
    def company_dashboard(self):
        return self._company_dashboard

    @property
    def company_ksef_settings(self):
        return self._company_ksef_settings

    @property
    def sessions(self) -> SessionRepository:
        return self._sessions

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def close(self) -> None:
        return None
