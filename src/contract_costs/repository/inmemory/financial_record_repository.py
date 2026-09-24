from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.financial_record import (
    FinancialRecord,
    FinancialRecordStatus,
)
from contract_costs.repository.financial_record_repository import (
    FinancialRecordRepository,
)
from contract_costs.repository.inmemory.financial_record_line_repository import (
    InMemoryFinancialRecordLineRepository,
)
from contract_costs.services.financial_records.review.dto.financial_record_review_query import (
    FinancialRecordReviewQuery,
)


class InMemoryFinancialRecordRepository(FinancialRecordRepository):

    def __init__(
        self,
        line_repository: InMemoryFinancialRecordLineRepository | None = None,
    ) -> None:
        self._records: dict[UUID, FinancialRecord] = {}
        self._line_repository = line_repository
        if line_repository is not None:
            line_repository.bind_record_deleted_check(self._is_deleted)

    def _is_deleted(self, record_id: UUID) -> bool:
        record = self._records.get(record_id)
        return record is not None and record.status == FinancialRecordStatus.DELETED

    # =====================================================
    # CREATE / UPDATE
    # =====================================================

    def add(self, record: FinancialRecord) -> None:
        self._records[record.id] = record

    def update(self, record: FinancialRecord) -> None:
        self._records[record.id] = record
        # =====================================================
        # DOCUMENTS
        # =====================================================

    # def add_document(self, document: Document) -> None:
    #     record = self._records.get(document.financial_record_id)
    #     if not record:
    #         return
    #
    #     if record.organization_id != document.organization_id:
    #         return
    #
    #     record.documents.append(document)
    #
    # def remove_document(
    #         self,
    #         *,
    #         organization_id: UUID,
    #         document_id: UUID,
    # ) -> None:
    #     for record in self._records.values():
    #         if record.organization_id != organization_id:
    #             continue
    #
    #         record.documents = [
    #             d for d in record.documents
    #             if d.id != document_id
    #         ]

    def has_documents(
            self,
            *,
            organization_id: UUID,
            record_id: UUID,
    ) -> bool:
        record = self._records.get(record_id)
        if not record or record.organization_id != organization_id:
            return False

        return bool(record.documents)
    # =====================================================
    # READ – single
    # =====================================================

    def get(
        self,
        *,
        organization_id: UUID,
        record_id: UUID,
    ) -> FinancialRecord | None:
        r = self._records.get(record_id)
        if not r or r.organization_id != organization_id:
            return None
        return r

    def get_record_dates(
        self,
        *,
        organization_id: UUID,
        record_ids: list[UUID],
    ) -> dict[UUID, date | None]:
        return {
            r.id: r.selling_date or r.invoice_date
            for record_id in record_ids
            if (r := self._records.get(record_id)) and r.organization_id == organization_id
        }

    def exists(
        self,
        *,
        organization_id: UUID,
        record_id: UUID,
    ) -> bool:
        r = self._records.get(record_id)
        return bool(r and r.organization_id == organization_id)

    # =====================================================
    # LOOKUP
    # =====================================================

    def get_by_reference(
        self,
        *,
        organization_id: UUID,
        reference: str,
    ) -> list[FinancialRecord]:
        return [
            r for r in self._records.values()
            if r.organization_id == organization_id
            and r.reference == reference
            and r.status != FinancialRecordStatus.DELETED
        ]

    def get_unique_record(
        self,
        *,
        organization_id: UUID,
        reference: str,
        seller_id: UUID,
    ) -> FinancialRecord | None:
        for r in self._records.values():
            if (
                r.organization_id == organization_id
                and r.reference == reference
                and r.seller_id == seller_id
                and r.status != FinancialRecordStatus.DELETED
            ):
                return r
        return None

    # =====================================================
    # LISTS
    # =====================================================

    def list_all(
        self,
        *,
        organization_id: UUID,
    ) -> list[FinancialRecord]:
        return [
            r for r in self._records.values()
            if r.organization_id == organization_id
        ]

    def list_by_seller_id(
        self,
        *,
        organization_id: UUID,
        seller_id: UUID,
    ) -> list[FinancialRecord]:
        return [
            r for r in self._records.values()
            if r.organization_id == organization_id
            and r.seller_id == seller_id
        ]

    def get_for_assignment(
        self,
        *,
        organization_id: UUID,
        status: FinancialRecordStatus | list[FinancialRecordStatus],
    ) -> list[FinancialRecord]:

        statuses = (
            {status}
            if isinstance(status, FinancialRecordStatus)
            else set(status)
        )

        return [
            r for r in self._records.values()
            if r.organization_id == organization_id
            and r.status in statuses
        ]

    # =====================================================
    # REVIEW QUERY
    # =====================================================

    def count_for_review(
        self,
        *,
        organization_id: UUID,
        query: FinancialRecordReviewQuery,
    ) -> int:
        return len(
            self._filtered_for_review(organization_id=organization_id, query=query)
        )

    def find_by_total(
        self,
        *,
        organization_id: UUID,
        total: Decimal,
        tolerance: Decimal,
        seller_id: UUID | None = None,
    ) -> list[UUID]:
        if not self._line_repository:
            return []

        matches: list[UUID] = []

        for r in self._records.values():
            if r.organization_id != organization_id:
                continue
            if r.status == FinancialRecordStatus.DELETED:
                continue
            if seller_id and r.seller_id != seller_id:
                continue

            lines = self._line_repository.list_by_financial_record(
                organization_id=organization_id,
                financial_record_id=r.id,
            )
            if not lines:
                continue

            record_total = sum((l.amount.gross for l in lines), Decimal("0"))
            if abs(record_total - total) <= tolerance:
                matches.append(r.id)

        return matches

    def _filtered_for_review(
        self,
        *,
        organization_id: UUID,
        query: FinancialRecordReviewQuery,
    ) -> list[FinancialRecord]:

        result = [
            r for r in self._records.values()
            if r.organization_id == organization_id
        ]

        if query.only_ready_for_accountant:
            result = [
                r for r in result
                if r.status == FinancialRecordStatus.PROCESSED
            ]

        elif query.statuses:
            result = [
                r for r in result
                if r.status in query.statuses
            ]

        else:
            result = [
                r for r in result
                if r.status != FinancialRecordStatus.DELETED
            ]

        if query.payment_statuses:
            result = [
                r for r in result
                if r.payment_status in query.payment_statuses
            ]

        if query.from_date:
            result = [
                r for r in result
                if r.invoice_date and r.invoice_date >= query.from_date
            ]

        if query.to_date:
            result = [
                r for r in result
                if r.invoice_date and r.invoice_date <= query.to_date
            ]

        return result

    def list_for_review(
        self,
        *,
        organization_id: UUID,
        query: FinancialRecordReviewQuery,
    ) -> list[FinancialRecord]:

        result = self._filtered_for_review(organization_id=organization_id, query=query)

        if query.payment_statuses:
            result = sorted(
                result,
                key=lambda r: (r.due_date, r.timestamp),
            )
        else:
            result = sorted(
                result,
                key=lambda r: (r.invoice_date or r.timestamp, r.timestamp),
                reverse=True,
            )

        if query.limit:
            result = result[:query.limit]

        return result
