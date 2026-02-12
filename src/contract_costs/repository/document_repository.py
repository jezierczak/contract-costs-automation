from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.model.document import Document


class DocumentRepository(ABC):

    @abstractmethod
    def add(self, document: Document) -> None: ...

    @abstractmethod
    def update(self, document: Document) -> None: ...

    @abstractmethod
    def get(
        self,
        *,
        organization_id: UUID,
        document_id: UUID,
    ) -> Document | None: ...

    @abstractmethod
    def delete(
        self,
        *,
        organization_id: UUID,
        document_id: UUID,
    ) -> None: ...

    @abstractmethod
    def list_unattached(
        self,
        *,
        organization_id: UUID,
    ) -> list[Document]: ...

    @abstractmethod
    def list_by_record_id(
        self,
        *,
        organization_id: UUID,
        record_id: UUID,
    ) -> list[Document]: ...

    @abstractmethod
    def attach_to_record(
        self,
        *,
        organization_id: UUID,
        document_id: UUID,
        record_id: UUID,
    ) -> None: ...

    @abstractmethod
    def exists_by_hash(
        self,
        *,
        organization_id: UUID,
        file_hash: str,
    ) -> bool: ...

    @abstractmethod
    def list_all(
            self,
            *,
            organization_id: UUID,
    ) -> list[Document]: ...

    @abstractmethod
    def list_filtered(
            self,
            *,
            organization_id: UUID,
            has_payload: bool | None = None,
            has_record: bool | None = None,
            document_source: str | None = None,
    ) -> list[Document]: ...