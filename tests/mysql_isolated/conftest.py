import os
import uuid
from pathlib import Path

import mysql.connector
import pytest

from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.repository.inmemory.document_repository import InMemoryDocumentRepository
from contract_costs.repository.inmemory.contract_node_repository import InMemoryContractNodeRepository
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
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
from contract_costs.repository.inmemory.snapshot.contract_snapshot_repository import (
    InMemoryContractSnapshotRepository,
)
from contract_costs.repository.inmemory.value_type_repository import InMemoryValueTypeRepository
from contract_costs.repository.mysql.contract_node_repository import MySQLContractNodeRepository
from contract_costs.repository.mysql.contract_repository import MySQLContractRepository
from contract_costs.repository.mysql.document_repository import MySQLDocumentRepository
from contract_costs.repository.mysql.financial_record_line_repository import MySQLFinancialRecordLineRepository
from contract_costs.repository.mysql.financial_record_repository import MySQLFinancialRecordRepository
from contract_costs.repository.mysql.identity.organization_repository import (
    MySqlOrganizationRepository,
)
from contract_costs.repository.mysql.identity.organization_user_repository import (
    MySqlOrganizationUserRepository,
)
from contract_costs.repository.mysql.identity.user_repository import MySqlUserRepository
from contract_costs.repository.mysql.number_sequence_repository import MySQLNumberSequenceRepository
from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
from contract_costs.repository.mysql.snapshot.contract_node_snapshot_repository import (
    MySQLContractNodeSnapshotRepository,
)
from contract_costs.repository.mysql.snapshot.contract_node_value_snapshot_repository import (
    MySQLContractNodeValueSnapshotRepository,
)
from contract_costs.repository.mysql.snapshot.contract_snapshot_repository import (
    MySQLContractSnapshotRepository,
)
from contract_costs.repository.mysql.value_type_repository import MySQLValueTypeRepository


pytestmark = pytest.mark.mysql_isolated


def _validate_isolated_target(*, host: str, database: str, user: str) -> None:
    if os.getenv("TEST_DB_ISOLATED") != "1":
        raise RuntimeError(
            "TEST_DB_ISOLATED=1 is required for mysql_isolated tests."
        )

    allowed_hosts = {"127.0.0.1", "localhost"}
    if host not in allowed_hosts:
        raise RuntimeError(f"Unsafe DB host for contract tests: {host}")

    if not database.startswith("test_"):
        raise RuntimeError(f"Unsafe DB name for contract tests: {database}")

    if user.lower() in {"prod", "production"}:
        raise RuntimeError(f"Unsafe DB user for contract tests: {user}")


@pytest.fixture(scope="session")
def mysql_contract_connection():
    tc = pytest.importorskip("testcontainers.mysql")
    MySqlContainer = tc.MySqlContainer

    db_name = f"test_{uuid.uuid4().hex[:12]}"
    mysql_user = "contract_tester"
    mysql_password = "contract_tester_pwd"
    mysql_image = os.getenv("MYSQL_CONTRACT_IMAGE", "mysql:8.4")

    container = MySqlContainer(
        image=mysql_image,
        username=mysql_user,
        password=mysql_password,
        dbname=db_name,
    )
    container.start()

    try:
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(3306))
        _validate_isolated_target(host=host, database=db_name, user=mysql_user)

        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=mysql_user,
            password=mysql_password,
            database=db_name,
        )
        try:
            schema_path = Path(__file__).parent / "schema" / "mysql_isolated_schema.sql"
            schema_sql = schema_path.read_text(encoding="utf-8")
            filtered_lines = []
            for line in schema_sql.splitlines():
                stripped = line.strip()
                if stripped.startswith("--"):
                    continue
                filtered_lines.append(line)
            schema_sql = "\n".join(filtered_lines)
            with conn.cursor() as cur:
                statements = [
                    stmt.strip()
                    for stmt in schema_sql.split(";")
                    if stmt.strip()
                ]
                for stmt in statements:
                    cur.execute(stmt)
            conn.commit()
            yield conn
        finally:
            conn.close()
    finally:
        container.stop()


@pytest.fixture(autouse=True)
def _cleanup_mysql_isolated_data(request):
    callspec = getattr(request.node, "callspec", None)
    if callspec is None:
        return

    uses_mysql = "mysql" in callspec.params.values()
    if not uses_mysql:
        return

    conn = request.getfixturevalue("mysql_contract_connection")
    with conn.cursor() as cur:
        cur.execute("DELETE FROM contract_node_value_snapshots")
        cur.execute("DELETE FROM contract_node_snapshots")
        cur.execute("DELETE FROM contract_snapshots")
        cur.execute("DELETE FROM contract_node_progress")
        cur.execute("DELETE FROM contract_nodes")
        cur.execute("DELETE FROM contracts")
        cur.execute("DELETE FROM financial_record_lines")
        cur.execute("DELETE FROM financial_records")
        cur.execute("DELETE FROM documents")
        cur.execute("DELETE FROM number_sequences")
        cur.execute("DELETE FROM value_types")
        cur.execute("DELETE FROM organization_users")
        cur.execute("DELETE FROM organizations")
        cur.execute("DELETE FROM users")
        cur.execute("DELETE FROM companies")
    conn.commit()


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def company_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryCompanyRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLCompanyRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def document_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryDocumentRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLDocumentRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def value_type_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryValueTypeRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLValueTypeRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def number_sequence_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryNumberSequenceRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLNumberSequenceRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def financial_record_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryFinancialRecordRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLFinancialRecordRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def financial_record_line_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryFinancialRecordLineRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLFinancialRecordLineRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def record_and_line_repos_contract(request):
    """Para repozytoriów rekordów i linii na wspólnym backendzie (do zapytań łączących obie tabele)."""
    backend = request.param
    if backend == "memory":
        line_repo = InMemoryFinancialRecordLineRepository()
        return InMemoryFinancialRecordRepository(line_repository=line_repo), line_repo
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return (
            MySQLFinancialRecordRepository(connection=mysql_contract_connection),
            MySQLFinancialRecordLineRepository(connection=mysql_contract_connection),
        )
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def contract_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryContractRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLContractRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def contract_node_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryContractNodeRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLContractNodeRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def contract_snapshot_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryContractSnapshotRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLContractSnapshotRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def contract_node_snapshot_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryContractNodeSnapshotRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLContractNodeSnapshotRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def contract_node_value_snapshot_repo_contract(request):
    backend = request.param
    if backend == "memory":
        return InMemoryContractNodeValueSnapshotRepository()
    if backend == "mysql":
        mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
        return MySQLContractNodeValueSnapshotRepository(connection=mysql_contract_connection)
    raise RuntimeError(f"Unsupported backend in contract tests: {backend}")


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def identity_storage_contract(request):
    if request.param == "memory":
        return InMemoryIdentityStorage()
    return None


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def organization_repo_contract(request, identity_storage_contract):
    backend = request.param
    if backend == "memory":
        return InMemoryOrganizationRepository(identity_storage_contract)
    mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
    return MySqlOrganizationRepository(connection=mysql_contract_connection)


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def user_repo_contract(request, identity_storage_contract):
    backend = request.param
    if backend == "memory":
        return InMemoryUserRepository(identity_storage_contract)
    mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
    return MySqlUserRepository(connection=mysql_contract_connection)


@pytest.fixture(params=["memory", "mysql"], ids=["memory", "mysql"])
def organization_user_repo_contract(request, identity_storage_contract):
    backend = request.param
    if backend == "memory":
        return InMemoryOrganizationUserRepository(identity_storage_contract)
    mysql_contract_connection = request.getfixturevalue("mysql_contract_connection")
    return MySqlOrganizationUserRepository(connection=mysql_contract_connection)
