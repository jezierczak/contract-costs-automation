from datetime import date
from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot
from contract_costs.repository.snapshot.contract_snapshot_repository import ContractSnapshotRepository


class MySQLContractSnapshotRepository(ContractSnapshotRepository):
    def __init__(self, connection=None) -> None:
        self._connection = connection

    def _get_connection(self):
        return self._connection or get_connection()

    def _maybe_commit(self, conn) -> None:
        if self._connection is None:
            conn.commit()

    def _maybe_rollback(self, conn) -> None:
        if self._connection is None:
            conn.rollback()

    def _maybe_close(self, conn) -> None:
        if self._connection is None:
            conn.close()

    def add(self, snapshot: ContractSnapshot) -> None:
        sql = """
              INSERT INTO contract_snapshots (id, organization_id, contract_id,
                                              snapshot_date, created_at, created_by_user_id)
              VALUES (%s, %s, %s, %s, %s, %s)
              """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(snapshot.id),
                        str(snapshot.organization_id),
                        str(snapshot.contract_id),
                        snapshot.snapshot_date,
                        snapshot.created_at,
                        snapshot.created_by_user_id,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def get(self, *, organization_id: UUID, snapshot_id: UUID) -> ContractSnapshot | None:
        sql = """
              SELECT *
              FROM contract_snapshots
              WHERE id = %s AND organization_id = %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(snapshot_id), str(organization_id)))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def get_by_contract_and_date(self, *, organization_id: UUID, contract_id: UUID, snapshot_date: date) -> ContractSnapshot | None:
        sql = """
              SELECT *
              FROM contract_snapshots
              WHERE organization_id = %s
                AND contract_id = %s
                AND snapshot_date = %s
              LIMIT 1
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), str(contract_id), snapshot_date))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def list_by_contract(self, *, organization_id: UUID, contract_id: UUID) -> list[ContractSnapshot]:
        sql = """
              SELECT *
              FROM contract_snapshots
              WHERE organization_id = %s
                AND contract_id = %s
              ORDER BY snapshot_date
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), str(contract_id)))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def list_all(self, *, organization_id: UUID) -> list[ContractSnapshot]:
        sql = """
              SELECT *
              FROM contract_snapshots
              WHERE organization_id = %s
              ORDER BY snapshot_date
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id),))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    @staticmethod
    def _map_row(row: dict) -> ContractSnapshot:
        return ContractSnapshot(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            contract_id=UUID(row["contract_id"]),
            snapshot_date=row["snapshot_date"],
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
        )
