from dataclasses import dataclass, replace

from enum import Enum
from uuid import UUID
from datetime import date, datetime

from contract_costs.model.base_entity import BaseEntity
from contract_costs.model.document import Document


class PaymentMethod(Enum):
    PRE_PAID = "pre_paid"
    BANK_TRANSFER = "bank_transfer"   # przelew
    CASH = "cash"                     # gotówka
    CARD = "card"                     # karta
    BLIK = "blik"                     # BLIK
    BON = "bon"                       # bon
    CHECK = "check"                   # czek
    CREDIT = "credit"                 # kredyt
    UNKNOWN = "unknown"


class PaymentStatus(Enum):
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    UNKNOWN = "unknown"


class FinancialRecordStatus(Enum):
    NEW_COST = "new_cost"
    NEW_REVENUE = "new_revenue"
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PROCESSED = "processed"
    DELETED = "deleted"
    SENT_TO_ACCOUNTANT ="sent_to_accountant"
    MODIFIED = "modified"
    # REFERENCE = "reference"


@dataclass(slots=True)
class FinancialRecord(BaseEntity):
    id: UUID

    reference: str
    invoice_date: date | None
    selling_date: date | None


    buyer_id: UUID
    seller_id: UUID

    payment_method: PaymentMethod
    due_date: date | None
    payment_status: PaymentStatus
    paid_date: date | None

    status: FinancialRecordStatus

    #scan_filename: str | None
    tags: set[str]

    timestamp: datetime
    documents: list[Document]


    def mark_paid(self,
                  *,
                  updated_at: datetime,
                  updated_by_user_id: UUID,
                  paid_at: date | None = None) -> "FinancialRecord":
        return replace(
            self,
            payment_status=PaymentStatus.PAID,
            paid_date=paid_at,
            updated_by_user_id=updated_by_user_id,
            updated_at=updated_at

        )

    def mark_partially_paid(self,
                  *,
                  updated_at: datetime,
                  updated_by_user_id: UUID,
                  paid_at: date | None = None) -> "FinancialRecord":
        return replace(
            self,
            payment_status=PaymentStatus.PARTIALLY_PAID,
            paid_date=paid_at,
            updated_by_user_id=updated_by_user_id,
            updated_at=updated_at

        )

    def mark_unpaid(self,
                    *,
                    updated_at: datetime,
                    updated_by_user_id: UUID,
                    ) -> "FinancialRecord":
        return replace(
            self,
            payment_status=PaymentStatus.UNPAID,
            paid_date=None,
            updated_by_user_id=updated_by_user_id,
            updated_at=updated_at
        )

    def mark_sent_to_accountant(self,
                    *,
                    updated_at: datetime,
                    updated_by_user_id: UUID
                                ) -> "FinancialRecord":
        return replace(
            self,
            status=FinancialRecordStatus.SENT_TO_ACCOUNTANT,
            updated_by_user_id=updated_by_user_id,
            updated_at=updated_at
        )

    def reopen(self,
                    *,
                    updated_at: datetime,
                    updated_by_user_id: UUID
               ) -> "FinancialRecord":
        return replace(
            self,
            status=FinancialRecordStatus.IN_PROGRESS,
            updated_by_user_id=updated_by_user_id,
            updated_at=updated_at
        )

    def delete(
            self,
            *,
            updated_at: datetime,
            updated_by_user_id: UUID,
    ) -> "FinancialRecord":
        return replace(
            self,
            status=FinancialRecordStatus.DELETED,
            updated_by_user_id=updated_by_user_id,
            updated_at=updated_at,
        )

    def to_in_progress(
            self,
            *,
            updated_at: datetime,
            updated_by_user_id: UUID,
    ) -> "FinancialRecord":
        return replace(
            self,
            status=FinancialRecordStatus.IN_PROGRESS,
            updated_by_user_id=updated_by_user_id,
            updated_at=updated_at,
        )