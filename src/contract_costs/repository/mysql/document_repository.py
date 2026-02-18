import json
from uuid import UUID

from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.model.document import Document
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.repository.mysql.document_mapper import map_row_to_document


class MySQLDocumentRepository(DocumentRepository):
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

    def add(self, document: Document) -> None:
        sql = """
            INSERT INTO documents (
                id, organization_id, financial_record_id, document_source,
                document_type, document_number, seller_nip, parsed_payload,
                file_hash, file_path, filename, mime_type, size,
                created_at, created_by_user_id, updated_at, updated_by_user_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(document.id),
                        str(document.organization_id),
                        str(document.financial_record_id) if document.financial_record_id else None,
                        document.document_source.value if document.document_source else None,
                        document.document_type.value if document.document_type else None,
                        document.document_number,
                        document.seller_nip,
                        json.dumps(document.parsed_payload) if document.parsed_payload else None,
                        document.file_hash,
                        document.file_path,
                        document.filename,
                        document.mime_type,
                        document.size,
                        document.created_at,
                        str(document.created_by_user_id) if document.created_by_user_id else None,
                        document.updated_at,
                        str(document.updated_by_user_id) if document.updated_by_user_id else None,
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def update(self, document: Document) -> None:
        sql = """
            UPDATE documents
            SET financial_record_id = %s,
                document_source     = %s,
                document_type       = %s,
                document_number     = %s,
                seller_nip          = %s,
                parsed_payload      = %s,
                file_hash           = %s,
                file_path           = %s,
                filename            = %s,
                mime_type           = %s,
                size                = %s,
                updated_at          = %s,
                updated_by_user_id  = %s
            WHERE id = %s
              AND organization_id = %s
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        str(document.financial_record_id) if document.financial_record_id else None,
                        document.document_source.value if document.document_source else None,
                        document.document_type.value if document.document_type else None,
                        document.document_number,
                        document.seller_nip,
                        json.dumps(document.parsed_payload) if document.parsed_payload else None,
                        document.file_hash,
                        document.file_path,
                        document.filename,
                        document.mime_type,
                        document.size,
                        document.updated_at,
                        str(document.updated_by_user_id) if document.updated_by_user_id else None,
                        str(document.id),
                        str(document.organization_id),
                    ),
                )
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def attach_to_record(self, *, organization_id: UUID, document_id: UUID, record_id: UUID) -> None:
        sql = """
            UPDATE documents
            SET financial_record_id = %s
            WHERE id = %s
              AND organization_id = %s
              AND financial_record_id IS NULL
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (str(record_id), str(document_id), str(organization_id)))
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def delete(self, *, organization_id: UUID, document_id: UUID) -> None:
        sql = """
            DELETE FROM documents
            WHERE id = %s
              AND organization_id = %s
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (str(document_id), str(organization_id)))
            self._maybe_commit(conn)
        except Exception:
            self._maybe_rollback(conn)
            raise
        finally:
            self._maybe_close(conn)

    def get(self, *, organization_id: UUID, document_id: UUID) -> Document | None:
        sql = """
            SELECT *
            FROM documents
            WHERE id = %s
              AND organization_id = %s
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(document_id), str(organization_id)))
                row = cur.fetchone()
            return self._map_row(row) if row else None
        finally:
            self._maybe_close(conn)

    def list_unattached(self, *, organization_id: UUID) -> list[Document]:
        sql = """
            SELECT *
            FROM documents
            WHERE organization_id = %s
              AND financial_record_id IS NULL
            ORDER BY created_at DESC
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id),))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def list_by_record_id(self, *, organization_id: UUID, record_id: UUID) -> list[Document]:
        sql = """
            SELECT *
            FROM documents
            WHERE organization_id = %s
              AND financial_record_id = %s
            ORDER BY created_at
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id), str(record_id)))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def exists_by_hash(self, *, organization_id: UUID, file_hash: str) -> bool:
        sql = """
            SELECT 1
            FROM documents
            WHERE organization_id = %s
              AND file_hash = %s
            LIMIT 1
        """

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (str(organization_id), file_hash))
                return cur.fetchone() is not None
        finally:
            self._maybe_close(conn)

    def list_all(self, *, organization_id: UUID) -> list[Document]:
        sql = """
            SELECT *
            FROM documents
            WHERE organization_id = %s
            ORDER BY created_at DESC
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(organization_id),))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    def list_filtered(
        self,
        *,
        organization_id: UUID,
        has_payload: bool | None = None,
        has_record: bool | None = None,
        document_source: str | None = None,
    ) -> list[Document]:
        conditions = ["organization_id = %s"]
        params: list[str] = [str(organization_id)]

        if has_payload is True:
            conditions.append("parsed_payload IS NOT NULL")
        elif has_payload is False:
            conditions.append("parsed_payload IS NULL")

        if has_record is True:
            conditions.append("financial_record_id IS NOT NULL")
        elif has_record is False:
            conditions.append("financial_record_id IS NULL")

        if document_source:
            conditions.append("document_source = %s")
            params.append(document_source)

        where_clause = " AND ".join(conditions)
        sql = f"""
            SELECT *
            FROM documents
            WHERE {where_clause}
            ORDER BY created_at DESC
        """

        conn = self._get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, tuple(params))
                rows = cur.fetchall()
            return [self._map_row(r) for r in rows]
        finally:
            self._maybe_close(conn)

    @staticmethod
    def _map_row(row: dict) -> Document:
        return map_row_to_document(row)
