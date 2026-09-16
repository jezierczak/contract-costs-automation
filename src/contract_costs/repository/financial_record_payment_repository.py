from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.model.financial_record_payment import FinancialRecordPayment


class FinancialRecordPaymentRepository(ABC):

    @abstractmethod
    def add(
        self,
        *,
        organization_id: UUID,
        payment: FinancialRecordPayment,
    ) -> None:
        ...

    @abstractmethod
    def get(
        self,
        *,
        organization_id: UUID,
        payment_id: UUID,
    ) -> FinancialRecordPayment | None:
        ...

    @abstractmethod
    def list_by_financial_record(
        self,
        *,
        organization_id: UUID,
        financial_record_id: UUID,
    ) -> list[FinancialRecordPayment]:
        ...

    @abstractmethod
    def delete(
        self,
        *,
        organization_id: UUID,
        payment_id: UUID,
    ) -> None:
        ...

    @abstractmethod
    def delete_all_by_financial_record(
        self,
        *,
        organization_id: UUID,
        financial_record_id: UUID,
    ) -> int:
        ...
