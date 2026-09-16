from uuid import UUID

from contract_costs.model.financial_record_payment import FinancialRecordPayment
from contract_costs.repository.financial_record_payment_repository import (
    FinancialRecordPaymentRepository,
)


class InMemoryFinancialRecordPaymentRepository(FinancialRecordPaymentRepository):

    def __init__(self) -> None:
        self._payments: dict[UUID, FinancialRecordPayment] = {}

    def add(
        self,
        *,
        organization_id: UUID,
        payment: FinancialRecordPayment,
    ) -> None:
        assert payment.organization_id == organization_id
        self._payments[payment.id] = payment

    def get(
        self,
        *,
        organization_id: UUID,
        payment_id: UUID,
    ) -> FinancialRecordPayment | None:
        payment = self._payments.get(payment_id)
        if not payment or payment.organization_id != organization_id:
            return None
        return payment

    def list_by_financial_record(
        self,
        *,
        organization_id: UUID,
        financial_record_id: UUID,
    ) -> list[FinancialRecordPayment]:
        return [
            p for p in self._payments.values()
            if p.organization_id == organization_id
            and p.financial_record_id == financial_record_id
        ]

    def delete(
        self,
        *,
        organization_id: UUID,
        payment_id: UUID,
    ) -> None:
        payment = self._payments.get(payment_id)
        if payment and payment.organization_id == organization_id:
            del self._payments[payment_id]

    def delete_all_by_financial_record(
        self,
        *,
        organization_id: UUID,
        financial_record_id: UUID,
    ) -> int:
        to_delete = [
            p.id for p in self._payments.values()
            if p.organization_id == organization_id
            and p.financial_record_id == financial_record_id
        ]
        for payment_id in to_delete:
            del self._payments[payment_id]
        return len(to_delete)
