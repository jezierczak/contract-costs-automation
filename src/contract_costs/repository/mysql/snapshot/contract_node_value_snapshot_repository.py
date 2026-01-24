from uuid import UUID

from contract_costs.model.snapshot.contract_node_value_snapshot import (
    ContractNodeValueSnapshot,
)
from contract_costs.repository.snapshot.contract_node_value_snapshot_repository import (
    ContractNodeValueSnapshotRepository,
)
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLContractNodeValueSnapshotRepository(
    ContractNodeValueSnapshotRepository
):
    def add_many(
            self,
            values: list[ContractNodeValueSnapshot],
    ) -> None:
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

        conn = get_connection()
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
        conn.commit()

    def list_by_node_snapshot(
            self,
            node_snapshot_id: UUID,
    ) -> list[ContractNodeValueSnapshot]:
        sql = """
              SELECT *
              FROM contract_node_value_snapshots
              WHERE node_snapshot_id = %s \
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(node_snapshot_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_snapshot(
            self,
            snapshot_id: UUID,
    ) -> list[ContractNodeValueSnapshot]:
        sql = """
              SELECT v.*
              FROM contract_node_value_snapshots v
                       JOIN contract_node_snapshots ns
                            ON ns.id = v.node_snapshot_id
              WHERE ns.snapshot_id = %s 
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(snapshot_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]



    def list_all(self) -> list[ContractNodeValueSnapshot]:
        sql = """
        SELECT *
        FROM contract_node_value_snapshots
        ORDER BY node_snapshot_id, value_type_id
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    # ---------- mapping ----------
    @staticmethod
    def _map_row(row: dict) -> ContractNodeValueSnapshot:
        return ContractNodeValueSnapshot(
            id=UUID(row["id"]),
            node_snapshot_id=UUID(row["node_snapshot_id"]),
            value_type_id=UUID(row["value_type_id"]),
            net=row["net"],
            vat=row["vat"],
            gross=row["gross"],
            non_deductible=row["non_deductible"]
        )
