from uuid import UUID
from datetime import date

from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot
from contract_costs.repository.snapshot.contract_snapshot_repository import (
    ContractSnapshotRepository,
)
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLContractSnapshotRepository(ContractSnapshotRepository):

    def add(self, snapshot: ContractSnapshot) -> None:
        sql = """
        INSERT INTO contract_snapshots (
            id,
            contract_id,
            snapshot_date,
            created_at
        )
        VALUES (%s, %s, %s, %s)
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(snapshot.id),
                    str(snapshot.contract_id),
                    snapshot.snapshot_date,
                    snapshot.created_at,
                ),
            )
        conn.commit()

    def get(self, snapshot_id: UUID) -> ContractSnapshot | None:
        sql = "SELECT * FROM contract_snapshots WHERE id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(snapshot_id),))
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def get_by_contract_and_date(
        self,
        *,
        contract_id: UUID,
        snapshot_date: date,
    ) -> ContractSnapshot | None:
        sql = """
        SELECT *
        FROM contract_snapshots
        WHERE contract_id = %s
          AND snapshot_date = %s
        LIMIT 1
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                sql,
                (str(contract_id), snapshot_date),
            )
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def list_by_contract(
        self,
        contract_id: UUID,
    ) -> list[ContractSnapshot]:
        sql = """
        SELECT *
        FROM contract_snapshots
        WHERE contract_id = %s
        ORDER BY snapshot_date
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(contract_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_all(self) -> list[ContractSnapshot]:
        sql = """
        SELECT *
        FROM contract_snapshots
        ORDER BY snapshot_date
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    # ---------- mapping ----------
    @staticmethod
    def _map_row(row: dict) -> ContractSnapshot:
        return ContractSnapshot(
            id=UUID(row["id"]),
            contract_id=UUID(row["contract_id"]),
            snapshot_date=row["snapshot_date"],
            created_at=row["created_at"],
        )
