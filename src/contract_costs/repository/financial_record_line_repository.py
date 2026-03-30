from datetime import date
from decimal import Decimal
from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.financial_record_line import FinancialRecordLine


class FinancialRecordLineRepository(ABC):

    # ============================
    # CREATE / UPDATE
    # ============================

    @abstractmethod
    def add(
        self,
        *,
        organization_id: UUID,
        line: FinancialRecordLine,
    ) -> None:
        ...

    @abstractmethod
    def update(
        self,
        *,
        organization_id: UUID,
        line: FinancialRecordLine,
    ) -> None:
        ...

    # ============================
    # READ – single
    # ============================

    @abstractmethod
    def get(
        self,
        *,
        organization_id: UUID,
        line_id: UUID,
    ) -> FinancialRecordLine | None:
        ...

    @abstractmethod
    def exists(
        self,
        *,
        organization_id: UUID,
        line_id: UUID,
    ) -> bool:
        ...

    # ============================
    # READ – lists
    # ============================

    @abstractmethod
    def list_all(
        self,
        *,
        organization_id: UUID,
    ) -> list[FinancialRecordLine]:
        ...

    @abstractmethod
    def list_by_financial_record(
        self,
        *,
        organization_id: UUID,
        financial_record_id: UUID,
    ) -> list[FinancialRecordLine]:
        ...

    @abstractmethod
    def list_by_financial_record_ids(
        self,
        *,
        organization_id: UUID,
        financial_records_ids: list[UUID],
    ) -> list[FinancialRecordLine]:
        ...

    @abstractmethod
    def list_by_contract(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
    ) -> list[FinancialRecordLine]:
        ...

    @abstractmethod
    def list_unassigned(
        self,
        *,
        organization_id: UUID,
    ) -> list[FinancialRecordLine]:
        """
        Lines without financial_record_id
        (technical helper, not business rule)
        """
        ...

    @abstractmethod
    def list_by_contract_until(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
        snapshot_date: date,
    ) -> list[FinancialRecordLine]:
        """
        Lines KNOWN to the system at snapshot_date
        (created_at <= snapshot_date)
        """
        ...

    # ============================
    # DELETE helpers
    # ============================

    @abstractmethod
    def delete_not_in_ids(
        self,
        *,
        organization_id: UUID,
        financial_record_id: UUID,
        keep_ids: set[UUID],
    ) -> int:
        ...

    @abstractmethod
    def find_financial_record_ids_by_line_amounts(
            self,
            *,
            organization_id: UUID,
            line_amounts: list[Decimal],
            expected: int,
            tolerance: Decimal,
    ) -> list[UUID]:
        """
        Returns financial_record_ids that contain lines matching
        all provided line_amounts (within tolerance).

        Duplicate amounts must be respected.
        """
        ...