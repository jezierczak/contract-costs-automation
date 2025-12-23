from uuid import UUID
from typing import Optional

from contract_costs.model.cost_type import CostType
from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLCostTypeRepository(CostTypeRepository):

    def add(self, cost_type: CostType) -> None:
        sql = """
        INSERT INTO cost_types (
            id,
            code,
            name,
            description,
            is_active
        ) VALUES (%s, %s, %s, %s, %s)
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(cost_type.id),
                        cost_type.code,
                        cost_type.name,
                        cost_type.description,
                        cost_type.is_active,
                    ),
                )
            conn.commit()

    def get(self, cost_type_id: UUID) -> Optional[CostType]:
        sql = """
        SELECT
            id,
            code,
            name,
            description,
            is_active
        FROM cost_types
        WHERE id = %s
        """

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(cost_type_id),))
                row = cur.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def get_by_code(self, code: str) -> Optional[CostType]:
        sql = """
        SELECT
            id,
            code,
            name,
            description,
            is_active
        FROM cost_types
        WHERE code = %s
        """

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (code,))
                row = cur.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def list(self) -> list[CostType]:
        sql = """
        SELECT
            id,
            code,
            name,
            description,
            is_active
        FROM cost_types
        ORDER BY code
        """

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql)
                rows = cur.fetchall()

        return [self._map_row(row) for row in rows]

    def update(self, cost_type: CostType) -> None:
        sql = """
        UPDATE cost_types
        SET
            code = %s,
            name = %s,
            description = %s,
            is_active = %s
        WHERE id = %s
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        cost_type.code,
                        cost_type.name,
                        cost_type.description,
                        cost_type.is_active,
                        str(cost_type.id),
                    ),
                )
            conn.commit()

    def exists(self, cost_type_id: UUID) -> bool:
        sql = """
        SELECT 1
        FROM cost_types
        WHERE id = %s
        LIMIT 1
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (str(cost_type_id),))
                row = cur.fetchone()

        return row is not None

    # -------------------------
    # internal helpers
    # -------------------------
    @staticmethod
    def _map_row(row: dict) -> CostType:
        return CostType(
            id=UUID(row["id"]),
            code=row["code"],
            name=row["name"],
            description=row["description"],
            is_active=bool(row["is_active"]),
        )
