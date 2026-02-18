from typing import Any

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from contract_costs.repository.mysql.contract_node_repository import MySQLContractNodeRepository
from contract_costs.repository.mysql.contract_repository import MySQLContractRepository
from contract_costs.repository.mysql.document_repository import MySQLDocumentRepository
from contract_costs.repository.mysql.financial_record_line_repository import MySQLFinancialRecordLineRepository
from contract_costs.repository.mysql.financial_record_repository import MySQLFinancialRecordRepository
from contract_costs.repository.mysql.identity.organization_repository import MySqlOrganizationRepository
from contract_costs.repository.mysql.identity.organization_user_repository import MySqlOrganizationUserRepository
from contract_costs.repository.mysql.identity.user_repository import MySqlUserRepository
from contract_costs.repository.mysql.number_sequence_repository import MySQLNumberSequenceRepository
from contract_costs.repository.mysql.snapshot.contract_node_snapshot_repository import (
    MySQLContractNodeSnapshotRepository,
)
from contract_costs.repository.mysql.snapshot.contract_node_value_snapshot_repository import (
    MySQLContractNodeValueSnapshotRepository,
)
from contract_costs.repository.mysql.snapshot.contract_snapshot_repository import MySQLContractSnapshotRepository
from contract_costs.repository.mysql.value_type_repository import MySQLValueTypeRepository
from contract_costs.unit_of_work.unit_of_work import UnitOfWork


class MySQLUnitOfWork(UnitOfWork):

    """
    MySQL UoW with a shared connection across repositories.
    Repositories run without local commits when the connection is injected.
    """

    def __init__(self) -> None:
        super().__init__()
        self._conn: Any = get_connection()
        self._companies = MySQLCompanyRepository(connection=self._conn)
        self._financial_records = MySQLFinancialRecordRepository(connection=self._conn)
        self._financial_record_lines = MySQLFinancialRecordLineRepository(connection=self._conn)
        self._contracts = MySQLContractRepository(connection=self._conn)
        self._contract_nodes = MySQLContractNodeRepository(connection=self._conn)
        self._value_types = MySQLValueTypeRepository(connection=self._conn)
        self._contract_snapshots = MySQLContractSnapshotRepository(connection=self._conn)
        self._contract_node_snapshots = MySQLContractNodeSnapshotRepository(connection=self._conn)
        self._contract_node_value_snapshots = MySQLContractNodeValueSnapshotRepository(connection=self._conn)
        self._organizations = MySqlOrganizationRepository(connection=self._conn)
        self._organization_users = MySqlOrganizationUserRepository(connection=self._conn)
        self._users = MySqlUserRepository(connection=self._conn)
        self._documents = MySQLDocumentRepository(connection=self._conn)
        self._number_sequences = MySQLNumberSequenceRepository(connection=self._conn)

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
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()
