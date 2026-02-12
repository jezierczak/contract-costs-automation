from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.contract_node import ContractNode
from contract_costs.model.contract_node_progress import ContractNodeProgress
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
              INSERT INTO contract_nodes (id, 
                                          organization_id, 
                                          contract_id, 
                                          parent_id, 
                                          code, 
                                          name, 
                                          budget, 
                                          quantity, 
                                          unit, 
                                          is_active, 
                                          created_at, 
                                          created_by_user_id)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
              """

        values = [
            (
                str(n.id),
                str(n.organization_id),
                str(n.contract_id),
                str(n.parent_id) if n.parent_id else None,
                n.code,
                n.name,
                n.budget,
                n.quantity,
                n.unit.value if n.unit else None,
                n.is_active,
                n.created_at,
                str(n.created_by_user_id),
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
            progress: ContractNodeProgress
    ) -> None:
        sql = """
              INSERT INTO contract_node_progress (id, 
                                                  organization_id, 
                                                  contract_node_id, 
                                                  progress_date, 
                                                  progress, 
                                                  created_at, 
                                                  created_by_user_id)
              SELECT %s, %s, %s, %s, %s, %s, %s
                    FROM contract_nodes
                    WHERE id = %s
                      AND organization_id = %s
              ON DUPLICATE KEY UPDATE progress           = VALUES(progress), 
                                      updated_at         = VALUES(created_at), 
                                      updated_by_user_id = VALUES(created_by_user_id)
              """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(progress.id),
                    str(progress.organization_id),
                    str(progress.contract_node_id),
                    progress.progress_date,
                    progress.progress,
                    progress.created_at,
                    progress.created_by_user_id,
                ),
            )
        conn.commit()
    # =========================================================
    # READ
    # =========================================================

    def get(
            self,
            *,
            organization_id: UUID,
            contract_node_id: UUID,
    ) -> ContractNode | None:
        sql = """
              SELECT *
              FROM contract_nodes
              WHERE id = %s
                AND organization_id = %s \
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(contract_node_id), str(organization_id)))
            row = cur.fetchone()

        if not row:
            return None

        node = self._map_row(row)
        self._attach_progress_history(organization_id, [node])
        return node

    def get_by_code(
        self,
        organization_id: UUID,
        contract_node_code: str
    ) -> ContractNode | None:
        sql = """
        SELECT *
        FROM contract_nodes
        WHERE code = %s
          AND organization_id = %s
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (contract_node_code, str(organization_id)))
            row = cur.fetchone()

        if not row:
            return None

        node = self._map_row(row)
        self._attach_progress_history(organization_id, [node])
        return node

    def list_nodes(
            self,
            *,
            organization_id: UUID,
    ) -> list[ContractNode]:
        sql = """
              SELECT *
              FROM contract_nodes
              WHERE organization_id = %s \
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(organization_id),))
            rows = cur.fetchall()

        nodes = [self._map_row(r) for r in rows]
        self._attach_progress_history(organization_id, nodes)
        return nodes

    def list_by_parent(
        self,
        *,
        organization_id: UUID,
        parent_id: UUID,
    ) -> list[ContractNode]:
        sql = """
        SELECT *
        FROM contract_nodes
        WHERE parent_id = %s
          AND organization_id = %s
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(parent_id), str(organization_id)))
            rows = cur.fetchall()

        nodes = [self._map_row(r) for r in rows]
        self._attach_progress_history(organization_id, nodes)
        return nodes

    def list_by_contract(
            self,
            *,
            organization_id: UUID,
            contract_id: UUID,
    ) -> list[ContractNode]:
        sql = """
              SELECT *
              FROM contract_nodes
              WHERE contract_id = %s
                AND organization_id = %s
              ORDER BY IF(parent_id IS NULL, 0, 1), code 
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(contract_id), str(organization_id)))
            rows = cur.fetchall()

        nodes = [self._map_row(r) for r in rows]
        self._attach_progress_history(organization_id, nodes)
        return nodes

    def list_leaf_nodes_for_active_contracts(
            self,
            *,
            organization_id: UUID,
    ) -> list[ContractNode]:
        sql = """
              SELECT cn.*
              FROM contract_nodes cn
                       JOIN contracts c
                            ON c.id = cn.contract_id
                                AND c.organization_id = cn.organization_id
                       LEFT JOIN contract_nodes child
                                 ON child.parent_id = cn.id
                                     AND child.organization_id = cn.organization_id
              WHERE cn.organization_id = %s
                AND child.id IS NULL
                AND c.status = 'active'
              ORDER BY SUBSTRING_INDEX(cn.code, '_', 1), 
                       cn.code 
              """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(organization_id),))
            rows = cur.fetchall()

        nodes = [self._map_row(r) for r in rows]
        self._attach_progress_history(organization_id, nodes)
        return nodes
    # =========================================================
    # UPDATE / DELETE
    # =========================================================

    def update(self, contract_node: ContractNode) -> None:
        sql = """
              UPDATE contract_nodes
              SET parent_id          = %s,
                  code               = %s,
                  name               = %s,
                  budget             = %s,
                  quantity           = %s,
                  unit               = %s,
                  is_active          = %s,
                  updated_at         = %s,
                  updated_by_user_id = %s
              WHERE id = %s
                AND organization_id = %s \
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
                    contract_node.updated_at,
                    contract_node.updated_by_user_id,
                    str(contract_node.id),
                    str(contract_node.organization_id),
                ),
            )
        conn.commit()

    def update_many(self, nodes: list[ContractNode]) -> None:
        for n in nodes:
            self.update(n)

    def delete_by_contract(
            self,
            *,
            organization_id: UUID,
            contract_id: UUID,
    ) -> None:
        sql = """
              DELETE 
              FROM contract_nodes
              WHERE contract_id = %s
                AND organization_id = %s 
              """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(contract_id), str(organization_id)))
        conn.commit()

    def delete_many(
            self,
            *,
            organization_id: UUID,
            ids: list[UUID],
    ) -> None:
        if not ids:
            return

        placeholders = ",".join(["%s"] * len(ids))
        sql = f"""
         DELETE FROM contract_nodes
         WHERE organization_id = %s
           AND id IN ({placeholders})
         """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(organization_id), *[str(i) for i in ids]))
        conn.commit()

    def exists(
            self,
            *,
            organization_id: UUID,
            contract_node_id: UUID,
    ) -> bool:
        sql = """
              SELECT 1
              FROM contract_nodes
              WHERE id = %s
                AND organization_id = %s
              LIMIT 1 \
              """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(contract_node_id), str(organization_id)))
            return cur.fetchone() is not None

    def has_values(
            self,
            *,
            organization_id: UUID,
            contract_id: UUID,
    ) -> bool:
        sql = """
              SELECT 1
              FROM financial_record_lines
              WHERE contract_id = %s
                AND organization_id = %s
              LIMIT 1 
              """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(contract_id), str(organization_id)))
            return cur.fetchone() is not None

    def node_has_values(
        self,
        *,
        organization_id: UUID,
        contract_node_id: UUID,
    ) -> bool:
        sql = """
        SELECT 1
        FROM financial_record_lines
        WHERE contract_node_id = %s
          AND organization_id = %s
        LIMIT 1
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(contract_node_id), str(organization_id)))
            return cur.fetchone() is not None
    # =========================================================
    # INTERNAL HELPERS
    # =========================================================

    @staticmethod
    def _map_row(row: dict) -> ContractNode:
        return ContractNode(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            contract_id=UUID(row["contract_id"]),
            parent_id=UUID(row["parent_id"]) if row["parent_id"] else None,
            code=row["code"],
            name=row["name"],
            budget=row["budget"],
            quantity=row["quantity"],
            unit=UnitOfMeasure(row["unit"]) if row["unit"] else None,
            is_active=row["is_active"],
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
            updated_at=row["updated_at"],
            updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
            progress_history={},
        )

    def _attach_progress_history(
            self,
            organization_id: UUID,
            nodes: list[ContractNode],
    ) -> None:
        if not nodes:
            return

        node_ids = [n.id for n in nodes]
        history = self._load_progress_history(organization_id, node_ids)

        for n in nodes:
            n.progress_history = history.get(n.id, {})

    @staticmethod
    def _load_progress_history(
            organization_id: UUID,
            node_ids: list[UUID],
    ) -> dict[UUID, dict[date, Decimal]]:
        if not node_ids:
            return {}

        placeholders = ",".join(["%s"] * len(node_ids))
        sql = f"""
           SELECT contract_node_id, progress_date, progress
           FROM contract_node_progress
           WHERE organization_id = %s
             AND contract_node_id IN ({placeholders})
           """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(organization_id), *[str(i) for i in node_ids]))
            rows = cur.fetchall()

        history: dict[UUID, dict[date, Decimal]] = {}

        for r in rows:
            nid = UUID(r["contract_node_id"])
            history.setdefault(nid, {})[r["progress_date"]] = r["progress"]

        return history