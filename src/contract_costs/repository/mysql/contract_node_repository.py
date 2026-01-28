from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from contract_costs.model.contract_node import ContractNode
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLContractNodeRepository(ContractNodeRepository):

    def add(self, contract_node: ContractNode) -> None:
        self.add_all([contract_node])

    def add_all(self, contract_nodes: list[ContractNode]) -> None:
        if not contract_nodes:
            return

        sql = """
        INSERT INTO contract_nodes (
            id, contract_id, parent_id,
            code, name,
            budget, quantity, unit,is_active
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
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
                n.is_active

            )
            for n in contract_nodes
        ]

        conn = get_connection()
        with conn.cursor() as cur:
            cur.executemany(sql, values)
        conn.commit()

    # =========================================================
    # PROGRESS
    # =========================================================

    def add_progress(
            self,
            node_id: UUID,
            progress: Decimal,
            progress_date: date,
    ) -> None:
        sql = """
              INSERT INTO contract_node_progress (id, 
                                                  contract_node_id, 
                                                  progress_date, 
                                                  progress)
              VALUES (%s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE progress   = VALUES(progress), 
                                      created_at = CURRENT_TIMESTAMP 
              """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(uuid4()),
                    str(node_id),
                    progress_date,
                    progress,
                ),
            )
        conn.commit()
    # =========================================================
    # READ
    # =========================================================

    def get(self, contract_node_id: UUID) -> ContractNode | None:
        sql = "SELECT * FROM contract_nodes WHERE id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(contract_node_id),))
            row = cur.fetchone()

        if not row:
            return None

        node = self._map_row_base(row)
        self._attach_progress_history([node])
        return node

    def get_by_code(self, contract_node_code: str) -> ContractNode | None:
        sql = "SELECT * FROM contract_nodes WHERE code = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (contract_node_code,))
            row = cur.fetchone()

        if not row:
            return None

        node = self._map_row_base(row)
        self._attach_progress_history([node])
        return node

    def list_nodes(self) -> list[ContractNode]:
        sql = "SELECT * FROM contract_nodes"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        nodes = [self._map_row_base(r) for r in rows]
        self._attach_progress_history(nodes)
        return nodes

    def list_by_parent(self, parent_id: UUID) -> list[ContractNode]:
        sql = "SELECT * FROM contract_nodes WHERE parent_id = %s"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(parent_id),))
            rows = cur.fetchall()

        nodes = [self._map_row_base(r) for r in rows]
        self._attach_progress_history(nodes)
        return nodes

    def list_by_contract(self, contract_id: UUID) -> list[ContractNode]:
        sql = """
              SELECT *
              FROM contract_nodes
              WHERE contract_id = %s
              ORDER BY IF(parent_id IS NULL, 0, 1), code \
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(contract_id),))
            rows = cur.fetchall()

        nodes = [self._map_row_base(r) for r in rows]
        self._attach_progress_history(nodes)
        return nodes


    def list_leaf_nodes_for_active_contracts(self) -> list[ContractNode]:
        sql = """
              SELECT cn.*
              FROM contract_nodes cn
                       JOIN contracts c ON c.id = cn.contract_id
                       LEFT JOIN contract_nodes child ON child.parent_id = cn.id
              WHERE child.id IS NULL
                AND c.status = "active" 
                  ORDER BY
                    SUBSTRING_INDEX(cn.code, '_', 1),
                        cn.code
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        nodes = [self._map_row_base(r) for r in rows]
        self._attach_progress_history(nodes)
        return nodes
    # =========================================================
    # UPDATE / DELETE
    # =========================================================



    def update(self, contract_node: ContractNode) -> None:
        sql = """
        UPDATE contract_nodes SET
            parent_id = %s,
            code = %s,
            name = %s,
            budget = %s,
            quantity = %s,
            unit = %s,
            is_active = %s
        WHERE id = %s
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(contract_node.parent_id) if contract_node.parent_id else None,
                    contract_node.code,
                    contract_node.name,
                    contract_node.budget,
                    contract_node.quantity,
                    contract_node.unit.value if contract_node.unit else None,
                    contract_node.is_active,
                    str(contract_node.id),
                ),
            )
        conn.commit()

    def update_many(self, nodes: list[ContractNode]) -> None:
        for n in nodes:
            self.update(n)

    def delete_by_contract(self, contract_id: UUID) -> None:
        sql = "DELETE FROM contract_nodes WHERE contract_id = %s"
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(contract_id),))
        conn.commit()

    def delete_many(self, ids: list[UUID]) -> None:
        if not ids:
            return

        placeholders = ",".join(["%s"] * len(ids))
        sql = f"DELETE FROM contract_nodes WHERE id IN ({placeholders})"

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, tuple(str(i) for i in ids))
        conn.commit()


    def exists(self, contract_node_id: UUID) -> bool:
        sql = "SELECT 1 FROM contract_nodes WHERE id = %s LIMIT 1"

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(contract_node_id),))
            return cur.fetchone() is not None

    def has_values(self, contract_id: UUID) -> bool:
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

    def node_has_values(self, contract_node_id: UUID) -> bool:
        sql = """
        SELECT 1
        FROM invoice_lines
        WHERE cost_node_id = %s
        LIMIT 1
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(contract_node_id),))
            return cur.fetchone() is not None
    # =========================================================
    # INTERNAL HELPERS
    # =========================================================

    @staticmethod
    def _map_row_base(row: dict) -> ContractNode:
        return ContractNode(
            id=UUID(row["id"]),
            contract_id=UUID(row["contract_id"]),
            parent_id=UUID(row["parent_id"]) if row["parent_id"] else None,
            code=row["code"],
            name=row["name"],
            budget=row["budget"],
            quantity=row["quantity"],
            unit=UnitOfMeasure(row["unit"]) if row["unit"] else None,
            is_active=row["is_active"],
            progress_history={},  # uzupełniane później
        )

    def _attach_progress_history(self, nodes: list[ContractNode]) -> None:
        if not nodes:
            return

        node_ids = [n.id for n in nodes]
        history_map = self._load_progress_history(node_ids)

        for n in nodes:
            n.progress_history = history_map.get(n.id, {})

    @staticmethod
    def _load_progress_history(
            node_ids: list[UUID],
    ) -> dict[UUID, dict[date, Decimal]]:
        if not node_ids:
            return {}

        placeholders = ",".join(["%s"] * len(node_ids))
        sql = f"""
            SELECT contract_node_id, progress_date, progress
            FROM contract_node_progress
            WHERE contract_node_id IN ({placeholders})
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, [str(i) for i in node_ids])
            rows = cur.fetchall()

        history: dict[UUID, dict[date, Decimal]] = {}

        for r in rows:
            nid = UUID(r["contract_node_id"])
            history.setdefault(nid, {})[r["progress_date"]] = r["progress"]

        return history