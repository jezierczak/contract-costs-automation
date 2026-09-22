import uuid
from typing import Any, Optional

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.document import (
    Document,
    DocumentType,
    DocumentSource,
    DocumentStatus,
    ScoringResult,
)


class DocumentBuilder:
    def __init__(self):
        now = utc_now()

        self._id = new_uuid()
        self._organization_id = new_uuid()
        self._created_at = now
        self._created_by_user_id = None
        self._updated_at = None
        self._updated_by_user_id = None

        self._financial_record_id = None
        self._document_status = DocumentStatus.NEW
        self._document_source = DocumentSource.PDF
        self._document_type = None
        self._document_number = None
        self._seller_nip = None
        self._parsed_payload = None

        self._file_hash = "abc123"
        self._file_path = "/tmp/test.pdf"
        self._filename = "test.pdf"
        self._mime_type = "application/pdf"
        self._size = 100
        self._scoring = None

    # =====================================================
    # BUILD
    # =====================================================

    def build(self) -> Document:
        return Document(
            id=self._id,
            organization_id=self._organization_id,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            financial_record_id=self._financial_record_id,
            document_status=self._document_status,
            document_source=self._document_source,
            document_type=self._document_type,
            document_number=self._document_number,
            seller_nip=self._seller_nip,
            parsed_payload=self._parsed_payload,
            file_hash=self._file_hash,
            file_path=self._file_path,
            filename=self._filename,
            mime_type=self._mime_type,
            size=self._size,
            scoring=self._scoring,
        )

    # =====================================================
    # BASE
    # =====================================================

    def with_id(self, id_: uuid.UUID) -> "DocumentBuilder":
        self._id = id_
        return self

    def with_organization_id(self, org_id: uuid.UUID) -> "DocumentBuilder":
        self._organization_id = org_id
        return self

    def with_financial_record_id(
        self,
        record_id: Optional[uuid.UUID],
    ) -> "DocumentBuilder":
        self._financial_record_id = record_id
        return self

    # =====================================================
    # DOCUMENT META
    # =====================================================

    def with_document_status(
        self,
        status: DocumentStatus,
    ) -> "DocumentBuilder":
        self._document_status = status
        return self

    def with_scoring(
        self,
        scoring: Optional[ScoringResult],
    ) -> "DocumentBuilder":
        self._scoring = scoring
        return self

    def with_document_source(
        self,
        source: DocumentSource,
    ) -> "DocumentBuilder":
        self._document_source = source
        return self

    def with_document_type(
        self,
        doc_type: Optional[DocumentType],
    ) -> "DocumentBuilder":
        self._document_type = doc_type
        return self

    def with_document_number(
        self,
        number: Optional[str],
    ) -> "DocumentBuilder":
        self._document_number = number
        return self

    def with_seller_nip(
        self,
        nip: Optional[str],
    ) -> "DocumentBuilder":
        self._seller_nip = nip
        return self

    def with_parsed_payload(
        self,
        payload: Optional[dict[str, Any]],
    ) -> "DocumentBuilder":
        self._parsed_payload = payload
        return self

    # =====================================================
    # FILE
    # =====================================================

    def with_file_hash(self, file_hash: str) -> "DocumentBuilder":
        self._file_hash = file_hash
        return self

    def with_file_path(self, path: str) -> "DocumentBuilder":
        self._file_path = path
        return self

    def with_filename(self, filename: str) -> "DocumentBuilder":
        self._filename = filename
        return self

    def with_mime_type(self, mime: Optional[str]) -> "DocumentBuilder":
        self._mime_type = mime
        return self

    def with_size(self, size: Optional[int]) -> "DocumentBuilder":
        self._size = size
        return self

    # =====================================================
    # AUDIT
    # =====================================================

    def with_updated_at(self, updated_at) -> "DocumentBuilder":
        self._updated_at = updated_at
        return self

    def with_updated_by(self, user_id: Optional[uuid.UUID]) -> "DocumentBuilder":
        self._updated_by_user_id = user_id
        return self
