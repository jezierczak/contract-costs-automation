from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.repository.financial_record_line_repository import (
    FinancialRecordLineRepository,
)


class InMemoryFinancialRecordLineRepository(FinancialRecordLineRepository):

    def __init__(self) -> None:
        self._lines: dict[UUID, FinancialRecordLine] = {}
        # ustawiane przez InMemoryFinancialRecordRepository — linie nie znają rekordów
        self._is_record_deleted: Callable[[UUID], bool] = lambda record_id: False

    def bind_record_deleted_check(self, is_record_deleted: Callable[[UUID], bool]) -> None:
        self._is_record_deleted = is_record_deleted

    def _belongs_to_active_record(self, line: FinancialRecordLine) -> bool:
        return (
            line.financial_record_id is None
            or not self._is_record_deleted(line.financial_record_id)
        )

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
            and self._belongs_to_active_record(l)
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
            and self._belongs_to_active_record(l)
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

    # =====================================================
    # MATCHING (uproszczone – bez uwzględnienia seller_id,
    # w przeciwieństwie do implementacji MySQL, która robi JOIN
    # do financial_records)
    # =====================================================

    def find_financial_record_ids_by_line_amounts(
        self,
        *,
        organization_id: UUID,
        line_amounts: list[Decimal],
        expected: int,
        tolerance: Decimal,
        seller_id: UUID | None = None,
    ) -> list[UUID]:
        if not line_amounts:
            return []

        counts: dict[UUID, int] = {}
        for line in self._lines.values():
            if line.organization_id != organization_id or line.financial_record_id is None:
                continue
            if any(abs(line.amount.value - amount) <= tolerance for amount in line_amounts):
                counts[line.financial_record_id] = counts.get(line.financial_record_id, 0) + 1

        return [record_id for record_id, count in counts.items() if count >= expected]

    def find_financial_record_ids_by_names(
        self,
        *,
        organization_id: UUID,
        names: list[str],
        expected: int,
        seller_id: UUID | None = None,
    ) -> list[UUID]:
        if not names:
            return []

        normalized_names = {n.strip().lower() for n in names}
        counts: dict[UUID, int] = {}
        for line in self._lines.values():
            if line.organization_id != organization_id or line.financial_record_id is None:
                continue
            if line.item_name.strip().lower() in normalized_names:
                counts[line.financial_record_id] = counts.get(line.financial_record_id, 0) + 1

        return [record_id for record_id, count in counts.items() if count >= expected]

    def find_financial_record_ids_by_names_and_quantities(
        self,
        *,
        organization_id: UUID,
        items: list[tuple[str, Decimal]],
        expected: int,
    ) -> list[UUID]:
        if not items:
            return []

        normalized_items = {(name.strip().lower(), quantity) for name, quantity in items}
        counts: dict[UUID, int] = {}
        for line in self._lines.values():
            if line.organization_id != organization_id or line.financial_record_id is None:
                continue
            key = (line.item_name.strip().lower(), line.quantity)
            if key in normalized_items:
                counts[line.financial_record_id] = counts.get(line.financial_record_id, 0) + 1

        return [record_id for record_id, count in counts.items() if count >= expected]
