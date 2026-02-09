from datetime import date, datetime
from uuid import UUID

from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.repository.financial_record_line_repository import (
    FinancialRecordLineRepository,
)


class InMemoryFinancialRecordLineRepository(FinancialRecordLineRepository):

    def __init__(self) -> None:
        self._lines: dict[UUID, FinancialRecordLine] = {}

    # =====================================================
    # CREATE / UPDATE
    # =====================================================

    def add(
        self,
        *,
        organization_id: UUID,
        line: FinancialRecordLine,
    ) -> None:
        assert line.organization_id == organization_id
        self._lines[line.id] = line

    def update(
        self,
        *,
        organization_id: UUID,
        line: FinancialRecordLine,
    ) -> None:
        assert line.organization_id == organization_id
        self._lines[line.id] = line

    # =====================================================
    # READ – single
    # =====================================================

    def get(
        self,
        *,
        organization_id: UUID,
        line_id: UUID,
    ) -> FinancialRecordLine | None:
        line = self._lines.get(line_id)
        if not line or line.organization_id != organization_id:
            return None
        return line

    def exists(
        self,
        *,
        organization_id: UUID,
        line_id: UUID,
    ) -> bool:
        return (
            line_id in self._lines
            and self._lines[line_id].organization_id == organization_id
        )

    # =====================================================
    # READ – lists
    # =====================================================

    def list_all(
        self,
        *,
        organization_id: UUID,
    ) -> list[FinancialRecordLine]:
        return [
            l for l in self._lines.values()
            if l.organization_id == organization_id
        ]

    def list_by_financial_record(
        self,
        *,
        organization_id: UUID,
        financial_record_id: UUID,
    ) -> list[FinancialRecordLine]:
        return [
            l for l in self._lines.values()
            if l.organization_id == organization_id
               and l.financial_record_id == financial_record_id
        ]

    def list_by_financial_record_ids(
        self,
        *,
        organization_id: UUID,
        financial_records_ids: list[UUID],
    ) -> list[FinancialRecordLine]:
        ids = set(financial_records_ids)
        return [
            l for l in self._lines.values()
            if l.organization_id == organization_id
            and l.financial_record_id in ids
        ]

    def list_by_contract(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
    ) -> list[FinancialRecordLine]:
        return [
            l for l in self._lines.values()
            if l.organization_id == organization_id
            and l.contract_id == contract_id
        ]

    def list_unassigned(
        self,
        *,
        organization_id: UUID,
    ) -> list[FinancialRecordLine]:
        """
        Lines without financial_record_id
        (technical helper, not business rule)
        """
        return [
            l for l in self._lines.values()
            if l.organization_id == organization_id
            and l.financial_record_id is None
        ]

    # =====================================================
    # SNAPSHOT / HISTORY
    # =====================================================

    def list_by_contract_until(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
        snapshot_date: date,
    ) -> list[FinancialRecordLine]:

        cutoff = datetime.combine(snapshot_date, datetime.max.time())

        return [
            l for l in self._lines.values()
            if l.organization_id == organization_id
            and l.contract_id == contract_id
            and l.created_at
            and l.created_at <= cutoff
        ]

    # =====================================================
    # DELETE helpers
    # =====================================================

    def delete_not_in_ids(
        self,
        *,
        organization_id: UUID,
        financial_record_id: UUID,
        keep_ids: set[UUID],
    ) -> int:
        to_delete: list[UUID] = []

        for line_id, line in self._lines.items():
            if line.organization_id != organization_id:
                continue

            if line.financial_record_id != financial_record_id:
                continue

            if keep_ids and line_id in keep_ids:
                continue

            to_delete.append(line_id)

        for line_id in to_delete:
            del self._lines[line_id]

        return len(to_delete)
