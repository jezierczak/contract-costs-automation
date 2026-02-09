from uuid import UUID
from typing import Dict, List

from contract_costs.model.document import Document
from contract_costs.repository.document_repository import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):

    def __init__(self) -> None:
        self._documents: Dict[UUID, Document] = {}

    # ============================================================
    # CREATE
    # ============================================================

    def add(self, document: Document) -> None:
        self._documents[document.id] = document

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, document: Document) -> None:
        if document.id not in self._documents:
            return
        self._documents[document.id] = document

    # ============================================================
    # READ
    # ============================================================

    def get(
        self,
        *,
        organization_id: UUID,
        document_id: UUID,
    ) -> Document | None:
        doc = self._documents.get(document_id)
        if not doc:
            return None
        if doc.organization_id != organization_id:
            return None
        return doc

    def list_unattached(
        self,
        *,
        organization_id: UUID,
    ) -> List[Document]:
        return [
            d for d in self._documents.values()
            if d.organization_id == organization_id
            and d.financial_record_id is None
        ]

    def list_by_record_id(
        self,
        *,
        organization_id: UUID,
        record_id: UUID,
    ) -> List[Document]:
        return [
            d for d in self._documents.values()
            if d.organization_id == organization_id
            and d.financial_record_id == record_id
        ]

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
        doc = self.get(
            organization_id=organization_id,
            document_id=document_id,
        )
        if not doc:
            return

        # symulacja warunku SQL: tylko jeśli NULL
        if doc.financial_record_id is None:
            doc.financial_record_id = record_id
            self._documents[document_id] = doc

    # ============================================================
    # DELETE
    # ============================================================

    def delete(
        self,
        *,
        organization_id: UUID,
        document_id: UUID,
    ) -> None:
        doc = self.get(
            organization_id=organization_id,
            document_id=document_id,
        )
        if doc:
            del self._documents[document_id]

    # ============================================================
    # HASH CHECK
    # ============================================================

    def exists_by_hash(
        self,
        *,
        organization_id: UUID,
        file_hash: str,
    ) -> bool:
        return any(
            d.organization_id == organization_id
            and d.file_hash == file_hash
            for d in self._documents.values()
        )
