from uuid import UUID

from contract_costs.model.cost_progress_snapshot import CostProgressSnapshot
from contract_costs.repository.cost_progress_snapshot_repository import CostProgressSnapshotRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLCostProgressSnapshotRepository(CostProgressSnapshotRepository):

    def add(self, snapshot: CostProgressSnapshot) -> None:
        sql = """
        INSERT INTO cost_progress_snapshots (
            id,
            contract_id,
            cost_node_id,
            snapshot_date,
            planned_amount,
            executed_amount,
            progress_percent
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(snapshot.id),
                    str(snapshot.contract_id),
                    str(snapshot.cost_node_id) if snapshot.cost_node_id else None,
                    snapshot.snapshot_date,
                    snapshot.planned_amount,
                    snapshot.executed_amount,
                    snapshot.progress_percent,
                ),
            )
        conn.commit()

    def get_by_contract(self, contract_id: UUID) -> list[CostProgressSnapshot]:
        sql = """
        SELECT *
        FROM cost_progress_snapshots
        WHERE contract_id = %s
        ORDER BY snapshot_date
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(contract_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def get_latest(
        self,
        contract_id: UUID,
        cost_node_id: UUID | None,
    ) -> CostProgressSnapshot | None:
        if cost_node_id is None:
            sql = """
            SELECT *
            FROM cost_progress_snapshots
            WHERE contract_id = %s
              AND cost_node_id IS NULL
            ORDER BY snapshot_date DESC
            LIMIT 1
            """
            params = (str(contract_id),)
        else:
            sql = """
            SELECT *
            FROM cost_progress_snapshots
            WHERE contract_id = %s
              AND cost_node_id = %s
            ORDER BY snapshot_date DESC
            LIMIT 1
            """
            params = (str(contract_id), str(cost_node_id))

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()

        return self._map_row(row) if row else None

    # ---------- mapping ----------
    @staticmethod
    def _map_row(row: dict) -> CostProgressSnapshot:
        return CostProgressSnapshot(
            id=UUID(row["id"]),
            contract_id=UUID(row["contract_id"]),
            cost_node_id=UUID(row["cost_node_id"]) if row["cost_node_id"] else None,
            snapshot_date=row["snapshot_date"],
            planned_amount=row["planned_amount"],
            executed_amount=row["executed_amount"],
            progress_percent=row["progress_percent"],
        )
