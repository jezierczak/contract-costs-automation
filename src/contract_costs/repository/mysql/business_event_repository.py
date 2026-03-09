import json
from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.business_event import BusinessEvent
from contract_costs.repository.business_event_repository import BusinessEventRepository


class MySQLBusinessEventRepository(BusinessEventRepository):

    def __init__(self, connection=None):
        self._connection = connection

    def _get_connection(self):
        return self._connection or get_connection()

    def _maybe_commit(self, conn):
        if self._connection is None:
            conn.commit()

    def _maybe_rollback(self, conn):
        if self._connection is None:
            conn.rollback()

    def _maybe_close(self, conn):
        if self._connection is None:
            conn.close()

    # ------------------------------------------------

    def add(self, event: BusinessEvent) -> None:

        sql = """
              INSERT INTO business_events (id, 
                                           organization_id, 
                                           type, 
                                           message, 
                                           entity_type, 
                                           entity_id, 
                                           created_at, 
                                           created_by_user_id)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
              """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(event.id),
                        str(event.organization_id),
                        event.type,
                        event.message,
                        event.entity_type,
                        str(event.entity_id) if event.entity_id else None,
                        event.created_at,
                        str(event.created_by_user_id)
                        if event.created_by_user_id else None,
                    ),
                )
            self._maybe_commit(conn)
        except:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    # ------------------------------------------------

    def list_recent(self, *, organization_id, limit=30):

        sql = """
              SELECT *
              FROM business_events
              WHERE organization_id = %s
              ORDER BY created_at DESC
              LIMIT %s \
              """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), limit))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    @staticmethod
    def _map_row(row):
        return BusinessEvent(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            type=row["type"],
            message=row["message"],
            entity_type=row["entity_type"],
            entity_id=UUID(row["entity_id"]) if row["entity_id"] else None,
            created_at=row["created_at"],
            created_by_user_id=UUID(row["created_by_user_id"])
            if row["created_by_user_id"] else None,
        )