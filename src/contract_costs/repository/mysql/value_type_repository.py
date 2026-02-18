from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.repository.value_type_repository import ValueTypeRepository


class MySQLValueTypeRepository(ValueTypeRepository):
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

    def add(self, value_type: ValueType) -> None:
        sql = """
        INSERT INTO value_types (
            id, organization_id, code, name, description, direction,
            is_active, created_at, created_by_user_id, updated_at, updated_by_user_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(value_type.id),
                        str(value_type.organization_id),
                        value_type.code,
                        value_type.name,
                        value_type.description,
                        value_type.direction.value,
                        value_type.is_active,
                        value_type.created_at,
                        str(value_type.created_by_user_id) if value_type.created_by_user_id else None,
                       value_type.updated_at,
                        str(value_type.updated_by_user_id) if value_type.updated_by_user_id else None,

                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def get(self, *, organization_id: UUID, value_type_id: UUID) -> ValueType | None:
        sql = """
        SELECT *
        FROM value_types
        WHERE id = %s
          AND organization_id = %s
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(value_type_id), str(organization_id)))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def get_by_code(self, organization_id: UUID, code: str) -> ValueType | None:
        sql = """
        SELECT *
        FROM value_types
        WHERE organization_id = %s
          AND code = %s
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), code))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def list_all(self, *, organization_id: UUID) -> list[ValueType]:
        sql = """
        SELECT *
        FROM value_types
        WHERE organization_id = %s
        ORDER BY code
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id),))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def list_active(self, *, organization_id: UUID) -> list[ValueType]:
        sql = """
        SELECT *
        FROM value_types
        WHERE organization_id = %s
          AND is_active = 1
        ORDER BY code
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id),))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def update(self, value_type: ValueType) -> None:
        sql = """
        UPDATE value_types
        SET
            name = %s,
            description = %s,
            direction = %s,
            is_active = %s,
            updated_at = %s,
            updated_by_user_id = %s
        WHERE id = %s
          AND organization_id = %s
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        value_type.name,
                        value_type.description,
                        value_type.direction.value,
                        value_type.is_active,
                        value_type.updated_at,
                        value_type.updated_by_user_id,
                        str(value_type.id),
                        str(value_type.organization_id),
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def exists(self, *, organization_id: UUID, value_type_id: UUID) -> bool:
        sql = """
        SELECT 1
        FROM value_types
        WHERE id = %s
          AND organization_id = %s
        LIMIT 1
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (str(value_type_id), str(organization_id)))
                return cur.fetchone() is not None
        finally:
            self._maybe_close(conn)

    @staticmethod
    def _map_row(row: dict) -> ValueType:
        return ValueType(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            code=row["code"],
            name=row["name"],
            description=row["description"],
            direction=ValueDirection(row["direction"]),
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
            updated_at=row["updated_at"],
            updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
        )
