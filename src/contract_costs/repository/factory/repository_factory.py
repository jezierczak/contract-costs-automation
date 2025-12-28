from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.repository.cost_progress_snapshot_repository import (
    CostProgressSnapshotRepository,
)

# mysql
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from contract_costs.repository.mysql.invoice_repository import MySQLInvoiceRepository
from contract_costs.repository.mysql.invoice_line_repository import MySQLInvoiceLineRepository
from contract_costs.repository.mysql.contract_repository import MySQLContractRepository
from contract_costs.repository.mysql.cost_node_repository import MySQLCostNodeRepository
from contract_costs.repository.mysql.cost_type_repository import MySQLCostTypeRepository
from contract_costs.repository.mysql.cost_progress_snapshot_repository import (
    MySQLCostProgressSnapshotRepository,
)

# in-memory
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository
from contract_costs.repository.inmemory.cost_type_repository import InMemoryCostTypeRepository
from contract_costs.repository.inmemory.cost_progress_snapshot_repository import (
    InMemoryCostProgressSnapshotRepository,
)
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

    def cost_node_repository(self) -> CostNodeRepository:
        return (
            MySQLCostNodeRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryCostNodeRepository()
        )

    def cost_type_repository(self) -> CostTypeRepository:
        return (
            MySQLCostTypeRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryCostTypeRepository()
        )

    def cost_progress_snapshot_repository(self) -> CostProgressSnapshotRepository:
        return (
            MySQLCostProgressSnapshotRepository()
            if self.backend == RepoBackend.MYSQL
            else InMemoryCostProgressSnapshotRepository()
        )
