from typing import Any
from uuid import UUID

from contract_costs.model.identity.user import User
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection


class MySqlUserRepository(UserRepository):

    # =========================================================
    # WRITE
    # =========================================================

    def add(self, user: User) -> None:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (
                    id,
                    login,
                    email,
                    full_name,
                    is_active,
                    created_at,
                    created_by_user_id,
                    updated_at,
                    updated_by_user_id,
                    password_hash,
                    last_login_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(user.id),
                    user.login,
                    user.email,
                    user.full_name,
                    user.is_active,
                    user.created_at,
                    str(user.created_by_user_id) if user.created_by_user_id else None,
                    user.updated_at,
                    str(user.updated_by_user_id) if user.updated_by_user_id else None,
                    user.password_hash,
                    user.last_login_at,
                ),
            )
        conn.commit()

    def update(self, user: User) -> None:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET
                    login = %s,
                    email = %s,
                    full_name = %s,
                    is_active = %s,
                    updated_at = %s,
                    updated_by_user_id = %s,
                    password_hash = %s,
                    last_login_at = %s
                WHERE id = %s
                """,
                (
                    user.login,
                    user.email,
                    user.full_name,
                    user.is_active,
                    user.updated_at,
                    str(user.updated_by_user_id) if user.updated_by_user_id else None,
                    user.password_hash,
                    user.last_login_at,
                    str(user.id),
                ),
            )
        conn.commit()

    # =========================================================
    # READ
    # =========================================================

    def get(self, user_id: UUID) -> User | None:
        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT * FROM users WHERE id = %s",
                (str(user_id),),
            )
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def get_by_login(self, login: str) -> User | None:
        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT * FROM users WHERE login = %s",
                (login,),
            )
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def list(self, *, active_only: bool = False) -> list[User]:
        sql = "SELECT * FROM users"
        params: list[Any] = []

        if active_only:
            sql += " WHERE is_active = TRUE"

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def exists(self, user_id: UUID) -> bool:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM users WHERE id = %s LIMIT 1",
                (str(user_id),),
            )
            return cur.fetchone() is not None

    # =========================================================
    # INTERNAL MAPPER
    # =========================================================

    @staticmethod
    def _map_row(row: dict) -> User:
        return User(
            id=UUID(row["id"]),
            login=row["login"],
            email=row["email"],
            full_name=row["full_name"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
            updated_at=row["updated_at"],
            updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
            password_hash=row["password_hash"],
            last_login_at=row["last_login_at"],
        )
