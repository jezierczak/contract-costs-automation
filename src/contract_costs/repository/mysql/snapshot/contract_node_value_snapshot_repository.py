from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.snapshot.contract_node_value_snapshot import ContractNodeValueSnapshot
from contract_costs.repository.snapshot.contract_node_value_snapshot_repository import ContractNodeValueSnapshotRepository


class MySQLContractNodeValueSnapshotRepository(ContractNodeValueSnapshotRepository):
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

    def add_many(self, values: list[ContractNodeValueSnapshot]) -> None:
        if not values:
            return

        sql = """
              INSERT INTO contract_node_value_snapshots (
                  id,
                  node_snapshot_id,
                  value_type_id,
                  net,
                  vat,
                  gross,
                  non_deductible
              )
              VALUES (%s, %s, %s, %s, %s, %s, %s)
              """

        rows = [
            (
                str(v.id),
                str(v.node_snapshot_id),
                str(v.value_type_id),
                v.net,
                v.vat,
                v.gross,
                v.non_deductible,
            )
            for v in values
        ]

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.executemany(sql, rows)
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def list_by_node_snapshot(self, node_snapshot_id: UUID) -> list[ContractNodeValueSnapshot]:
        sql = """
              SELECT *
              FROM contract_node_value_snapshots
              WHERE node_snapshot_id = %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(node_snapshot_id),))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def list_by_snapshot(self, snapshot_id: UUID) -> list[ContractNodeValueSnapshot]:
        sql = """
              SELECT v.*
              FROM contract_node_value_snapshots v
                       JOIN contract_node_snapshots ns
                            ON ns.id = v.node_snapshot_id
              WHERE ns.snapshot_id = %s
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(snapshot_id),))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def list_all(self) -> list[ContractNodeValueSnapshot]:
        sql = """
        SELECT *
        FROM contract_node_value_snapshots
        ORDER BY node_snapshot_id, value_type_id
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    @staticmethod
    def _map_row(row: dict) -> ContractNodeValueSnapshot:
        return ContractNodeValueSnapshot(
            id=UUID(row["id"]),
            node_snapshot_id=UUID(row["node_snapshot_id"]),
            value_type_id=UUID(row["value_type_id"]),
            net=row["net"],
            vat=row["vat"],
            gross=row["gross"],
            non_deductible=row["non_deductible"],
        )
