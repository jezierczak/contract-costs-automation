from datetime import datetime
from typing import Any
from uuid import UUID

from contract_costs.model.auth.session import Session
from contract_costs.repository.session_repository import SessionRepository


class MySQLSessionRepository(SessionRepository):

    def __init__(self, connection:Any = None):
        self._conn = connection

    def add(self, session: Session) -> None:
        sql = """
        INSERT INTO sessions (
            id,
            user_id,
            organization_id,
            created_at,
            expires_at
        )
        VALUES (%s, %s, %s, %s, %s)
        """

        with self._conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(session.id),
                    str(session.user_id),
                    str(session.organization_id) if session.organization_id else None,
                    session.created_at,
                    session.expires_at,
                ),
            )

    def get(self, session_id: UUID) -> Session | None:
        sql = """
        SELECT id, user_id, organization_id, created_at, expires_at
        FROM sessions
        WHERE id = %s
        """

        with self._conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(session_id),))
            row = cur.fetchone()

        if not row:
            return None

        return Session(
            id=UUID(row["id"]),
            user_id=UUID(row["user_id"]),
            organization_id=UUID(row["organization_id"])
            if row["organization_id"]
            else None,
            created_at=row["created_at"],
            expires_at=row["expires_at"],
        )

    def delete(self, session_id: UUID) -> None:
        sql = "DELETE FROM sessions WHERE id = %s"

        with self._conn.cursor() as cur:
            cur.execute(sql, (str(session_id),))

    def update(self, session: Session) -> None:
        sql = """
        UPDATE sessions
        SET organization_id = %s,
            expires_at = %s
        WHERE id = %s
        """

        with self._conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(session.organization_id)
                    if session.organization_id
                    else None,
                    session.expires_at,
                    str(session.id),
                ),
            )

    def delete_expired(self, now: datetime) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                "DELETE FROM sessions WHERE expires_at < %s",
                (now,),
            )
