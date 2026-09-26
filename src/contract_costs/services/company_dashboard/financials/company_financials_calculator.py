from datetime import date
from decimal import Decimal
from typing import Iterable
from uuid import UUID

from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.company_dashboard.dto.company_ledger_line_raw import CompanyLedgerLineRaw
from contract_costs.services.common.pillars import Pillars
from contract_costs.services.company_dashboard.financials.company_financials import (
    CompanyFinancials,
    CompanyPeriodFinancials,
    CompanyValueTypeFinancials,
)

EMPTY = CompanyPeriodFinancials()

MONTH_NAMES = [
    "", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
    "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień",
]


def period_range(year: int, month: int | None) -> tuple[date, date]:
    """Zakres [start, end) — cały rok albo jeden miesiąc."""
    if month is None:
        return date(year, 1, 1), date(year + 1, 1, 1)
    if month == 12:
        return date(year, 12, 1), date(year + 1, 1, 1)
    return date(year, month, 1), date(year, month + 1, 1)

# tylko rekordy, które przeszły walidację przypisania — walidacja jest bramką dla liczb
APPROVED_STATUSES = frozenset({
    FinancialRecordStatus.PROCESSED.value,
    FinancialRecordStatus.SENT_TO_ACCOUNTANT.value,
})


class CompanyFinancialsCalculator:
    """
    Jedno źródło prawdy dla finansów firmy own (dashboard, rozbicie, koszty stałe).

    Stronę linii wyznacza typ kosztu (tak jak walidacja przypisania):
    REVENUE → przychód, COST → koszt, FIXED → koszt i koszt stały.
    INTERNAL bierze stronę z faktury: sprzedawca → przychód, nabywca → koszt.
    Linia liczy się tylko wtedy, gdy firma stoi po właściwej stronie faktury.
    Koszty stałe są wyłącznie zewnętrzne — między firmami own walidacja
    wymusza INTERNAL, bo to nie jest realny wypływ z grupy.
    """

    @classmethod
    def calculate(
        cls,
        *,
        year: int,
        company_id: UUID,
        lines: Iterable[CompanyLedgerLineRaw],
    ) -> CompanyFinancials:

        total = EMPTY
        months: dict[int, CompanyPeriodFinancials] = {}
        unapproved: set[str] = set()

        for line in lines:
            if not cls.is_approved(line):
                unapproved.add(str(line.record_id))
                continue

            period = cls.classify(line=line, company_id=company_id)
            if period is None:
                continue

            total += period
            month = line.record_date.month
            months[month] = months.get(month, EMPTY) + period

        return CompanyFinancials(
            year=year,
            total=total,
            months=months,
            unapproved_record_count=len(unapproved),
        )

    @classmethod
    def breakdown(
        cls,
        *,
        company_id: UUID,
        lines: Iterable[CompanyLedgerLineRaw],
    ) -> list[CompanyValueTypeFinancials]:

        groups: dict[str | None, CompanyValueTypeFinancials] = {}

        for line in lines:
            if not cls.is_approved(line):
                continue

            period = cls.classify(line=line, company_id=company_id)
            if period is None:
                continue

            current = groups.get(line.value_type_id)
            groups[line.value_type_id] = CompanyValueTypeFinancials(
                value_type_id=line.value_type_id,
                code=line.value_type_code,
                name=line.value_type_name,
                is_fixed=(
                    line.direction == ValueDirection.FIXED.value
                    or cls._is_legacy_system_cost(line=line, company=str(company_id))
                ),
                financials=(current.financials if current else EMPTY) + period,
            )

        return list(groups.values())

    # =====================================================
    # LINE
    # =====================================================

    @staticmethod
    def is_approved(line: CompanyLedgerLineRaw) -> bool:
        return line.status in APPROVED_STATUSES

    @classmethod
    def classify(
        cls,
        *,
        line: CompanyLedgerLineRaw,
        company_id: UUID,
    ) -> CompanyPeriodFinancials | None:

        company = str(company_id)
        is_buyer = str(line.buyer_id) == company
        is_seller = str(line.seller_id) == company
        pillars = Pillars.of(cls.amount(line))

        if cls._is_legacy_system_cost(line=line, company=company):
            return CompanyPeriodFinancials(cost=pillars, fixed=pillars)

        match line.direction:
            case ValueDirection.FIXED.value if is_buyer:
                return CompanyPeriodFinancials(cost=pillars, fixed=pillars)
            case ValueDirection.COST.value if is_buyer:
                return CompanyPeriodFinancials(cost=pillars)
            case ValueDirection.REVENUE.value if is_seller:
                return CompanyPeriodFinancials(revenue=pillars)
            case ValueDirection.INTERNAL.value if is_seller:
                return CompanyPeriodFinancials(revenue=pillars)
            case ValueDirection.INTERNAL.value if is_buyer:
                return CompanyPeriodFinancials(cost=pillars)

        # typ kosztu niezgodny ze stroną faktury — rekord nie przeszedłby walidacji
        return None

    @classmethod
    def classify_against(
        cls,
        *,
        line: CompanyLedgerLineRaw,
        counterparty_id: UUID,
    ) -> CompanyPeriodFinancials | None:
        """Linia z perspektywy naszej strony faktury (tej, która nie jest kontrahentem)."""
        counterparty = str(counterparty_id)

        if str(line.buyer_id) == counterparty:
            our_side = line.seller_id
        elif str(line.seller_id) == counterparty:
            our_side = line.buyer_id
        else:
            return None

        return cls.classify(line=line, company_id=our_side)

    @staticmethod
    def _is_legacy_system_cost(*, line: CompanyLedgerLineRaw, company: str) -> bool:
        # LEGACY: koszty stałe księgowane na kontrakcie systemowym firmy
        return (
            line.contract_type == "system"
            and str(line.contract_owner_id) == company
            and line.direction != ValueDirection.REVENUE.value
        )

    @staticmethod
    def amount(line: CompanyLedgerLineRaw) -> Amount:
        return Amount.from_input(
            value=Decimal(line.amount_value),
            input_type=AmountInputType(line.amount_input_type),
            vat_rate=VatRate(Decimal(line.vat_rate)),
            tax_treatment=TaxTreatment(line.tax_treatment),
        )
