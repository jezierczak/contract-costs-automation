from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.financial_record import FinancialRecord, FinancialRecordStatus
from contract_costs.services.financial_records.review.dto.financial_record_review_query import FinancialRecordReviewQuery


class FinancialRecordRepository(ABC):

    # =====================================================
    # CREATE / UPDATE
    # =====================================================

    @abstractmethod
    def add(self, record: FinancialRecord) -> None:
        """Persist new financial record"""
        ...

    @abstractmethod
    def update(self, record: FinancialRecord) -> None:
        """Update existing financial record"""
        ...
        # =====================================================
        # DOCUMENTS (attachments)
        # =====================================================

    # @abstractmethod
    # def add_document(self, document: Document) -> None:
    #     """Attach document to financial record"""
    #     ...
    #
    # @abstractmethod
    # def remove_document(
    #         self,
    #         *,
    #         organization_id: UUID,
    #         document_id: UUID,
    # ) -> None:
    #     """Remove document from financial record"""
    #     ...

    @abstractmethod
    def has_documents(
            self,
            *,
            organization_id: UUID,
            record_id: UUID,
    ) -> bool:
        """Check if financial record has any documents attached"""
        ...
    # =====================================================
    # READ – single
    # =====================================================

    @abstractmethod
    def get(
            self,
            *,
            organization_id: UUID,
            record_id: UUID,
    ) -> FinancialRecord | None:
        ...

    @abstractmethod
    def exists(
            self,
            *,
            organization_id: UUID,
            record_id: UUID,
    ) -> bool:
        ...


    # =====================================================
    # READ – lookup
    # =====================================================

    @abstractmethod
    def get_by_reference(
            self,
            *,
            organization_id: UUID,
            reference: str,
    ) -> list[FinancialRecord]:
        ...

    @abstractmethod
    def get_unique_record(
            self,
            *,
            organization_id: UUID,
            reference: str,
            seller_id: UUID,
    ) -> FinancialRecord | None:
        ...

    # =====================================================
    # READ – lists
    # =====================================================

    @abstractmethod
    def list_all(
            self,
            *,
            organization_id: UUID,
    ) -> list[FinancialRecord]:
        ...

    @abstractmethod
    def list_by_seller_id(
            self,
            *,
            organization_id: UUID,
            seller_id: UUID,
    ) -> list[FinancialRecord]:
        ...

    @abstractmethod
    def get_for_assignment(
            self,
            *,
            organization_id: UUID,
            status: FinancialRecordStatus | list[FinancialRecordStatus],
    ) -> list[FinancialRecord]:
        """
        Return records that require assignment
        (status NEW or IN_PROGRESS)
        """
        ...

    @abstractmethod
    def list_for_review(
            self,
            *,
            organization_id: UUID,
            query: FinancialRecordReviewQuery,
    ) -> list[FinancialRecord]:
        ...

    @abstractmethod
    def count_for_review(
            self,
            *,
            organization_id: UUID,
            query: FinancialRecordReviewQuery,
    ) -> int:
        ...