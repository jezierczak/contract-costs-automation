from datetime import date, datetime
from typing import Optional
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.financial_record import (
    FinancialRecord,
    PaymentMethod,
    PaymentStatus,
    FinancialRecordStatus,
)
from contract_costs.model.document import Document


class FinancialRecordBuilder:
    def __init__(self):
        now = utc_now()

        self._id = new_uuid()
        self._organization_id = new_uuid()
        self._created_at = now
        self._created_by_user_id = None
        self._updated_at = None
        self._updated_by_user_id = None

        self._reference = "FV/1/2025"
        self._invoice_date = date.today()
        self._selling_date = date.today()

        self._buyer_id = new_uuid()
        self._seller_id = new_uuid()

        self._payment_method = PaymentMethod.BANK_TRANSFER
        self._due_date = None
        self._payment_status = PaymentStatus.UNPAID
        self._paid_date = None

        self._status = FinancialRecordStatus.NEW_COST

        self._tags = set()
        self._timestamp = now
        self._documents: list[Document] = []

    # =====================================================
    # BUILD
    # =====================================================

    def build(self) -> FinancialRecord:
        return FinancialRecord(
            id=self._id,
            organization_id=self._organization_id,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            reference=self._reference,
            invoice_date=self._invoice_date,
            selling_date=self._selling_date,
            buyer_id=self._buyer_id,
            seller_id=self._seller_id,
            payment_method=self._payment_method,
            due_date=self._due_date,
            payment_status=self._payment_status,
            paid_date=self._paid_date,
            status=self._status,
            tags=self._tags,
            timestamp=self._timestamp,
            documents=self._documents,
        )

    # =====================================================
    # BASE
    # =====================================================

    def with_id(self, id_: UUID) -> "FinancialRecordBuilder":
        self._id = id_
        return self

    def with_organization_id(self, org_id: UUID) -> "FinancialRecordBuilder":
        self._organization_id = org_id
        return self

    def with_created_at(self, created_at: datetime) -> "FinancialRecordBuilder":
        self._created_at = created_at
        return self

    def with_updated_at(self, updated_at: datetime) -> "FinancialRecordBuilder":
        self._updated_at = updated_at
        return self

    # =====================================================
    # IDENTITY
    # =====================================================

    def with_reference(self, reference: str) -> "FinancialRecordBuilder":
        self._reference = reference
        return self

    def with_invoice_date(self, invoice_date: Optional[date]) -> "FinancialRecordBuilder":
        self._invoice_date = invoice_date
        return self

    def with_selling_date(self, selling_date: Optional[date]) -> "FinancialRecordBuilder":
        self._selling_date = selling_date
        return self

    def with_buyer_id(self, buyer_id: UUID) -> "FinancialRecordBuilder":
        self._buyer_id = buyer_id
        return self

    def with_seller_id(self, seller_id: UUID) -> "FinancialRecordBuilder":
        self._seller_id = seller_id
        return self

    # =====================================================
    # PAYMENT
    # =====================================================

    def with_payment_method(self, method: PaymentMethod) -> "FinancialRecordBuilder":
        self._payment_method = method
        return self

    def with_due_date(self, due_date: Optional[date]) -> "FinancialRecordBuilder":
        self._due_date = due_date
        return self

    def with_payment_status(self, status: PaymentStatus) -> "FinancialRecordBuilder":
        self._payment_status = status
        return self

    def with_paid_date(self, paid_date: Optional[date]) -> "FinancialRecordBuilder":
        self._paid_date = paid_date
        return self

    # =====================================================
    # STATUS
    # =====================================================

    def with_status(self, status: FinancialRecordStatus) -> "FinancialRecordBuilder":
        self._status = status
        return self

    # =====================================================
    # META
    # =====================================================

    def with_tags(self, tags: set[str]) -> "FinancialRecordBuilder":
        self._tags = tags
        return self

    def with_timestamp(self, timestamp: datetime) -> "FinancialRecordBuilder":
        self._timestamp = timestamp
        return self

    def with_documents(self, documents: list[Document]) -> "FinancialRecordBuilder":
        self._documents = documents
        return self
