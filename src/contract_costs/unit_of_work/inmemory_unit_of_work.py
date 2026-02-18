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
from contract_costs.repository.inmemory.snapshot.contract_node_snapshot_repository import (
    InMemoryContractNodeSnapshotRepository,
)
from contract_costs.repository.inmemory.snapshot.contract_node_value_snapshot_repository import (
    InMemoryContractNodeValueSnapshotRepository,
)
from contract_costs.repository.inmemory.snapshot.contract_snapshot_repository import InMemoryContractSnapshotRepository
from contract_costs.repository.inmemory.value_type_repository import InMemoryValueTypeRepository
from contract_costs.unit_of_work.unit_of_work import UnitOfWork


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        super().__init__()
        identity_storage = InMemoryIdentityStorage()

        self._companies = InMemoryCompanyRepository()
        self._financial_records = InMemoryFinancialRecordRepository()
        self._financial_record_lines = InMemoryFinancialRecordLineRepository()
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

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def close(self) -> None:
        return None
