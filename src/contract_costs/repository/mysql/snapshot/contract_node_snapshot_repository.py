from uuid import UUID

from contract_costs.model.snapshot.contract_node_snapshot import (
    ContractNodeSnapshot,
)
from contract_costs.repository.snapshot.contract_node_snapshot_repository import (
    ContractNodeSnapshotRepository,
)
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLContractNodeSnapshotRepository(
    ContractNodeSnapshotRepository
):

    def add_many(
        self,
        snapshots: list[ContractNodeSnapshot],
    ) -> None:
        if not snapshots:
            return

        sql = """
        INSERT INTO contract_node_snapshots (
            id,
            snapshot_id,
            contract_node_id,
            planned_budget,
            progress
        )
        VALUES (%s, %s, %s, %s, %s)
        """

        values = [
            (
                str(s.id),
                str(s.snapshot_id),
                str(s.contract_node_id),
                s.planned_budget,
                s.progress,
            )
            for s in snapshots
        ]

        conn = get_connection()
        with conn.cursor() as cur:
            cur.executemany(sql, values)
        conn.commit()

    def get(
        self,
        node_snapshot_id: UUID,
    ) -> ContractNodeSnapshot | None:
        sql = """
        SELECT *
        FROM contract_node_snapshots
        WHERE id = %s
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(node_snapshot_id),))
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def list_by_snapshot(
        self,
        snapshot_id: UUID,
    ) -> list[ContractNodeSnapshot]:
        sql = """
        SELECT *
        FROM contract_node_snapshots
        WHERE snapshot_id = %s
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(snapshot_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_all(self) -> list[ContractNodeSnapshot]:
        sql = """
              SELECT *
              FROM contract_node_snapshots
              ORDER BY snapshot_id, contract_node_id \
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def get_root_by_snapshot(
            self,
            snapshot_id: UUID,
    ) -> ContractNodeSnapshot | None:
        sql = """
              SELECT ns.*
              FROM contract_node_snapshots ns
                       JOIN contract_nodes n
                            ON n.id = ns.contract_node_id
              WHERE ns.snapshot_id = %s
                AND n.parent_id IS NULL
              LIMIT 1 \
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(snapshot_id),))
            row = cur.fetchone()

        return self._map_row(row) if row else None

    # ---------- mapping ----------
    @staticmethod
    def _map_row(row: dict) -> ContractNodeSnapshot:
        return ContractNodeSnapshot(
            id=UUID(row["id"]),
            snapshot_id=UUID(row["snapshot_id"]),
            contract_node_id=UUID(row["contract_node_id"]),
            planned_budget=row["planned_budget"],
            progress=row["progress"],
        )
