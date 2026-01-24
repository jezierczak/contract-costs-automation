from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.repository.snapshot.contract_node_snapshot_repository import ContractNodeSnapshotRepository
from contract_costs.repository.snapshot.contract_node_value_snapshot_repository import \
    ContractNodeValueSnapshotRepository
from contract_costs.repository.snapshot.contract_snapshot_repository import ContractSnapshotRepository



# mysql
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from contract_costs.repository.mysql.invoice_repository import MySQLInvoiceRepository
from contract_costs.repository.mysql.invoice_line_repository import MySQLInvoiceLineRepository
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
from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository
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

    def invoice_repository(self) -> InvoiceRepository:
        return (
            MySQLInvoiceRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryInvoiceRepository()
        )

    def invoice_line_repository(self) -> InvoiceLineRepository:
        return (
            MySQLInvoiceLineRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryInvoiceLineRepository()
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
