from uuid import UUID
from typing import Iterable

from contract_costs.model.cost_node import CostNode
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLCostNodeRepository(CostNodeRepository):

    def add(self, cost_node: CostNode) -> None:
        self.add_all([cost_node])

    def add_all(self, cost_nodes: list[CostNode]) -> None:
        if not cost_nodes:
            return

        sql = """
        INSERT INTO cost_nodes (
            id, contract_id, parent_id,
            code, name,
            budget, quantity, unit
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = [
            (
                str(n.id),
                str(n.contract_id),
                str(n.parent_id) if n.parent_id else None,
                n.code,
                n.name,
                n.budget,
                n.quantity,
                n.unit.value if n.unit else None,
            )
            for n in cost_nodes
        ]

        conn = get_connection()
        with conn.cursor() as cur:
            cur.executemany(sql, values)
        conn.commit()

    def get(self, cost_node_id: UUID) -> CostNode | None:
        sql = "SELECT * FROM cost_nodes WHERE id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(cost_node_id),))
            row = cur.fetchone()

        return self._map_row(row) if row else None


    def get_by_code(self, cost_node_code: str) -> CostNode | None:
        sql = "SELECT * FROM cost_nodes WHERE code = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(cost_node_code),))
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def list_nodes(self) -> list[CostNode]:
        sql = "SELECT * FROM cost_nodes"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_parent(self, parent_id: UUID) -> list[CostNode]:
        sql = "SELECT * FROM cost_nodes WHERE parent_id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(parent_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_contract(self, contract_id: UUID) -> list[CostNode]:
        sql = """
              SELECT *
              FROM cost_nodes
              WHERE contract_id = %s
              ORDER BY IF(parent_id IS NULL, 0, 1), code 
              """
        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:

            cur.execute(sql, (str(contract_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def update(self, cost_node: CostNode) -> None:
        sql = """
        UPDATE cost_nodes SET
            parent_id = %s,
            code = %s,
            name = %s,
            budget = %s,
            quantity = %s,
            unit = %s
        WHERE id = %s
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(cost_node.parent_id) if cost_node.parent_id else None,
                    cost_node.code,
                    cost_node.name,
                    cost_node.budget,
                    cost_node.quantity,
                    cost_node.unit.value if cost_node.unit else None,
                    str(cost_node.id),
                ),
            )
        conn.commit()

    def update_many(self, nodes: list[CostNode]) -> None:
        for n in nodes:
            self.update(n)

    def delete_by_contract(self, contract_id: UUID) -> None:
        sql = "DELETE FROM cost_nodes WHERE contract_id = %s"

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(contract_id),))
        conn.commit()

    def delete_many(self, ids: list[UUID]) -> None:
        sql = "DELETE FROM cost_nodes WHERE id IN (%s)"

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(ids),))
        conn.commit()

    def exists(self, cost_node_id: UUID) -> bool:
        sql = "SELECT 1 FROM cost_nodes WHERE id = %s LIMIT 1"

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(cost_node_id),))
            return cur.fetchone() is not None

    def has_costs(self, contract_id: UUID) -> bool:
        sql = """
        SELECT 1
        FROM invoice_lines
        WHERE contract_id = %s
        LIMIT 1
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(contract_id),))
            return cur.fetchone() is not None

    def node_has_costs(self, cost_node_id: UUID) -> bool:
        sql = """
        SELECT 1
        FROM invoice_lines
        WHERE cost_node_id = %s
        LIMIT 1
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(cost_node_id),))
            return cur.fetchone() is not None

    # ---------- mapping ----------
    @staticmethod
    def _map_row( row: dict) -> CostNode:
        return CostNode(
            id=UUID(row["id"]),
            contract_id=UUID(row["contract_id"]),
            parent_id=UUID(row["parent_id"]) if row["parent_id"] else None,
            code=row["code"],
            name=row["name"],
            budget=row["budget"],
            quantity=row["quantity"],
            unit=UnitOfMeasure(row["unit"]) if row["unit"] else None,  # jeśli Enum → zmapuj
            is_active=row["is_active"]
        )
