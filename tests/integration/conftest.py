# from __future__ import annotations
#
# import pytest
# import mysql.connector
#
# from contract_costs.infrastructure.db.mysql_connection import get_connection
# from contract_costs.repository.mysql.company_repository import MySQLCompanyRepository
# from contract_costs.repository.mysql.contract_node_repository import MySQLContractNodeRepository
# from contract_costs.repository.mysql.contract_repository import MySQLContractRepository
# from contract_costs.repository.mysql.document_repository import MySQLDocumentRepository
# from contract_costs.repository.mysql.financial_record_line_repository import (
#     MySQLFinancialRecordLineRepository,
# )
# from contract_costs.repository.mysql.financial_record_repository import (
#     MySQLFinancialRecordRepository,
# )
# from contract_costs.repository.mysql.snapshot.contract_node_snapshot_repository import (
#     MySQLContractNodeSnapshotRepository,
# )
# from contract_costs.repository.mysql.snapshot.contract_node_value_snapshot_repository import (
#     MySQLContractNodeValueSnapshotRepository,
# )
# from contract_costs.repository.mysql.snapshot.contract_snapshot_repository import (
#     MySQLContractSnapshotRepository,
# )
# from contract_costs.repository.mysql.identity.organization_repository import (
#     MySqlOrganizationRepository,
# )
# from contract_costs.repository.mysql.value_type_repository import MySQLValueTypeRepository
#
#
# REQUIRED_TABLES = {
#     "companies",
#     "contracts",
#     "contract_nodes",
#     "value_types",
#     "financial_records",
#     "financial_record_lines",
#     "documents",
#     "contract_snapshots",
#     "contract_node_snapshots",
#     "contract_node_value_snapshots",
# }
#
# CLEANUP_ORDER = [
#     "contract_node_value_snapshots",
#     "contract_node_snapshots",
#     "contract_snapshots",
#     "financial_record_lines",
#     "documents",
#     "financial_records",
#     "contract_node_progress",
#     "contract_nodes",
#     "contracts",
#     "value_types",
#     "companies",
# ]
#
#
# def _load_existing_tables(conn) -> set[str]:
#     with conn.cursor() as cur:
#         cur.execute("SHOW TABLES")
#         rows = cur.fetchall()
#     return {row[0] for row in rows}
#
#
# def _clean_tables(conn, tables: set[str]) -> None:
#     with conn.cursor() as cur:
#         cur.execute("SET FOREIGN_KEY_CHECKS=0")
#         for table in CLEANUP_ORDER:
#             if table in tables:
#                 cur.execute(f"DELETE FROM `{table}`")
#         cur.execute("SET FOREIGN_KEY_CHECKS=1")
#     conn.commit()
#
#
# @pytest.fixture()
# def mysql_repo_bundle():
#     try:
#         conn = get_connection()
#     except mysql.connector.Error as exc:
#         pytest.skip(f"MySQL unavailable: {exc}")
#
#     try:
#         existing_tables = _load_existing_tables(conn)
#         missing = REQUIRED_TABLES - existing_tables
#         if missing:
#             pytest.skip(
#                 "MySQL schema missing required tables: "
#                 + ", ".join(sorted(missing))
#             )
#
#         _clean_tables(conn, existing_tables)
#     finally:
#         conn.close()
#
#     bundle = {
#         "company_repo": MySQLCompanyRepository(),
#         "organization_repo": MySqlOrganizationRepository(),
#         "contract_repo": MySQLContractRepository(),
#         "contract_node_repo": MySQLContractNodeRepository(),
#         "value_type_repo": MySQLValueTypeRepository(),
#         "record_repo": MySQLFinancialRecordRepository(),
#         "line_repo": MySQLFinancialRecordLineRepository(),
#         "document_repo": MySQLDocumentRepository(),
#         "snapshot_repo": MySQLContractSnapshotRepository(),
#         "node_snapshot_repo": MySQLContractNodeSnapshotRepository(),
#         "value_snapshot_repo": MySQLContractNodeValueSnapshotRepository(),
#     }
#
#     yield bundle
#
#     conn = get_connection()
#     try:
#         existing_tables = _load_existing_tables(conn)
#         _clean_tables(conn, existing_tables)
#     finally:
#         conn.close()
