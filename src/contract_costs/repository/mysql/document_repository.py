import json
from uuid import UUID

from contract_costs.model.document import (
    Document,
    DocumentType,
    DocumentSource,
)
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.infrastructure.db.mysql_connection import get_connection
from contract_costs.repository.mysql.document_mapper import map_row_to_document


class MySQLDocumentRepository(DocumentRepository):

    # ============================================================
    # CREATE
    # ============================================================

    def add(self, document: Document) -> None:
        sql = """
            INSERT INTO documents (
                id,
                organization_id,
                financial_record_id,
                document_source,
                document_type,
                document_number,
                seller_nip,
                parsed_payload,
                file_hash,
                file_path,
                filename,
                mime_type,
                size,
                created_at,
                created_by_user_id,
                updated_at,
                updated_by_user_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        conn = get_connection()
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
        conn.commit()

    # ============================================================
    # UPDATE
    # ============================================================

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

        conn = get_connection()
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
        conn.commit()

    # ============================================================
    # ATTACH
    # ============================================================

    def attach_to_record(
        self,
        *,
        organization_id: UUID,
        document_id: UUID,
        record_id: UUID,
    ) -> None:
        sql = """
            UPDATE documents
            SET financial_record_id = %s
            WHERE id = %s
              AND organization_id = %s
              AND financial_record_id IS NULL
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    str(record_id),
                    str(document_id),
                    str(organization_id),
                ),
            )
        conn.commit()

    # ============================================================
    # DELETE
    # ============================================================

    def delete(
        self,
        *,
        organization_id: UUID,
        document_id: UUID,
    ) -> None:
        sql = """
            DELETE FROM documents
            WHERE id = %s
              AND organization_id = %s
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(document_id), str(organization_id)))
        conn.commit()

    # ============================================================
    # READ
    # ============================================================

    def get(
        self,
        *,
        organization_id: UUID,
        document_id: UUID,
    ) -> Document | None:
        sql = """
            SELECT *
            FROM documents
            WHERE id = %s
              AND organization_id = %s
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(document_id), str(organization_id)))
            row = cur.fetchone()

        return self._map_row(row) if row else None

    def list_unattached(
        self,
        *,
        organization_id: UUID,
    ) -> list[Document]:
        sql = """
            SELECT *
            FROM documents
            WHERE organization_id = %s
              AND financial_record_id IS NULL
            ORDER BY created_at DESC
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (str(organization_id),))
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def list_by_record_id(
        self,
        *,
        organization_id: UUID,
        record_id: UUID,
    ) -> list[Document]:
        sql = """
            SELECT *
            FROM documents
            WHERE organization_id = %s
              AND financial_record_id = %s
            ORDER BY created_at
        """

        conn = get_connection()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                sql,
                (str(organization_id), str(record_id)),
            )
            rows = cur.fetchall()

        return [self._map_row(r) for r in rows]

    def exists_by_hash(
        self,
        *,
        organization_id: UUID,
        file_hash: str,
    ) -> bool:
        sql = """
            SELECT 1
            FROM documents
            WHERE organization_id = %s
              AND file_hash = %s
            LIMIT 1
        """

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (str(organization_id), file_hash))
            return cur.fetchone() is not None

    # ============================================================
    # MAPPING
    # ============================================================

    @staticmethod
    def _map_row(row: dict) -> Document:
        return map_row_to_document(row)