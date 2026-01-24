from uuid import UUID

from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySQLValueTypeRepository(ValueTypeRepository):

    def add(self, value_type: ValueType) -> None:
        sql = """
        INSERT INTO value_types (
            id,
            code,
            name,
            description,
            direction,
            is_active
        ) VALUES (%s, %s, %s, %s, %s,%s)
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(value_type.id),
                        value_type.code,
                        value_type.name,
                        value_type.description,
                        value_type.direction.value,
                        value_type.is_active,
                    ),
                )
            conn.commit()

    def get(self, value_type_id: UUID) -> ValueType | None:
        sql = """
        SELECT
            id,
            code,
            name,
            description,
            direction,
            is_active
        FROM value_types
        WHERE id = %s
        """

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(value_type_id),))
                row = cur.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def get_by_code(self, code: str) -> ValueType | None:
        sql = """
        SELECT
            id,
            code,
            name,
            description,
            direction,
            is_active
        FROM value_types
        WHERE code = %s
        """

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (code,))
                row = cur.fetchone()

        if row is None:
            return None

        return self._map_row(row)

    def list(self) -> list[ValueType]:
        sql = """
        SELECT
            id,
            code,
            name,
            description,
            direction,
            is_active
        FROM value_types
        ORDER BY code
        """

        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql)
                rows = cur.fetchall()

        return [self._map_row(row) for row in rows]

    def update(self, value_type: ValueType) -> None:
        sql = """
        UPDATE value_types
        SET
            code = %s,
            name = %s,
            description = %s,
            direction= %s,
            is_active = %s
        WHERE id = %s
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        value_type.code,
                        value_type.name,
                        value_type.description,
                        value_type.direction.value,
                        value_type.is_active,
                        str(value_type.id),
                    ),
                )
            conn.commit()

    def exists(self, value_type_id: UUID) -> bool:
        sql = """
        SELECT 1
        FROM value_types
        WHERE id = %s
        LIMIT 1
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (str(value_type_id),))
                row = cur.fetchone()

        return row is not None

    # -------------------------
    # internal helpers
    # -------------------------
    @staticmethod
    def _map_row(row: dict) -> ValueType:
        return ValueType(
            id=UUID(row["id"]),
            code=row["code"],
            name=row["name"],
            description=row["description"],
            direction=ValueDirection(row["direction"]),
            is_active=bool(row["is_active"]),
        )
