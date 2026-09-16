from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.financial_record_payment import FinancialRecordPayment


class FinancialRecordPaymentBuilder:
    def __init__(self):
        now = utc_now()

        self._id = new_uuid()
        self._organization_id = new_uuid()
        self._created_at = now
        self._created_by_user_id = None
        self._updated_at = None
        self._updated_by_user_id = None

        self._financial_record_id = new_uuid()
        self._amount = Decimal("100.00")
        self._paid_date = date.today()

    def build(self) -> FinancialRecordPayment:
        return FinancialRecordPayment(
            id=self._id,
            organization_id=self._organization_id,
            created_at=self._created_at,
            created_by_user_id=self._created_by_user_id,
            updated_at=self._updated_at,
            updated_by_user_id=self._updated_by_user_id,
            financial_record_id=self._financial_record_id,
            amount=self._amount,
            paid_date=self._paid_date,
        )

    def with_id(self, id_: UUID) -> "FinancialRecordPaymentBuilder":
        self._id = id_
        return self

    def with_organization_id(self, org_id: UUID) -> "FinancialRecordPaymentBuilder":
        self._organization_id = org_id
        return self

    def with_financial_record_id(self, record_id: UUID) -> "FinancialRecordPaymentBuilder":
        self._financial_record_id = record_id
        return self

    def with_amount(self, amount: Decimal) -> "FinancialRecordPaymentBuilder":
        self._amount = amount
        return self

    def with_paid_date(self, paid_date: Optional[date]) -> "FinancialRecordPaymentBuilder":
        self._paid_date = paid_date
        return self
