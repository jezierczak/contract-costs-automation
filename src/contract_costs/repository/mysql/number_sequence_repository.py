from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.number_sequence import NumberSequence
from contract_costs.repository.number_sequence_repository import NumberSequenceRepository


class MySQLNumberSequenceRepository(NumberSequenceRepository):
    def __init__(self, connection=None) -> None:
        self._connection = connection

    # def _resolve_connection(self, conn):
    #     return conn or self._connection or get_connection()
    #
    # def _is_owned(self, conn) -> bool:
    #     return conn is None and self._connection is None

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

    def get_for_update(self, organization_id: UUID, scope_key: str) -> NumberSequence | None:
        # resolved_conn = self._get_connection()
        # own_connection = self._is_owned(conn)
        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM number_sequences
                    WHERE organization_id = %s
                      AND scope_key = %s
                    FOR UPDATE
                    """,
                    (str(organization_id), scope_key),
                )
                row = cur.fetchone()
            if not row:
                return None
            return NumberSequence(
                organization_id=UUID(row["organization_id"]),
                scope_key=row["scope_key"],
                current_value=row["current_value"],
            )
        finally:
            self._maybe_close(conn)

    def add(self, sequence: NumberSequence) -> None:
        # resolved_conn = self._resolve_connection(conn)
        # own_connection = self._is_owned(conn)
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO number_sequences (
                        organization_id,
                        scope_key,
                        current_value,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s, NOW(6), NOW(6))
                    """,
                    (
                        str(sequence.organization_id),
                        sequence.scope_key,
                        sequence.current_value,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def update(self, sequence: NumberSequence) -> None:
        # resolved_conn = self._resolve_connection(conn)
        # own_connection = self._is_owned(conn)
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE number_sequences
                    SET current_value = %s,
                        updated_at = NOW(6)
                    WHERE organization_id = %s
                      AND scope_key = %s
                    """,
                    (
                        sequence.current_value,
                        str(sequence.organization_id),
                        sequence.scope_key,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)
