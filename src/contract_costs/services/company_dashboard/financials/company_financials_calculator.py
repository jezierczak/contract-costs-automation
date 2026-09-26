from decimal import Decimal
from typing import Iterable
from uuid import UUID

from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.company_dashboard.dto.company_ledger_line_raw import CompanyLedgerLineRaw
from contract_costs.services.common.pillars import Pillars
from contract_costs.services.company_dashboard.financials.company_financials import (
    CompanyFinancials,
    CompanyPeriodFinancials,
    CompanyValueTypeFinancials,
)

EMPTY = CompanyPeriodFinancials()


class CompanyFinancialsCalculator:
    """
    Jedno źródło prawdy dla finansów firmy own (dashboard, rozbicie, koszty stałe).

    Strona linii wynika z roli firmy na fakturze: sprzedawca → przychód,
    nabywca → koszt. Dotyczy też INTERNAL (bez eliminacji między firmami own).
    Koszty stałe (FIXED albo legacy kontrakt systemowy firmy) zawsze są kosztem
    i dodatkowo trafiają do filaru `fixed`.
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

        for line in lines:
            period = cls.classify(line=line, company_id=company_id)
            if period is None:
                continue

            total += period
            month = line.record_date.month
            months[month] = months.get(month, EMPTY) + period

        return CompanyFinancials(year=year, total=total, months=months)

    @classmethod
    def breakdown(
        cls,
        *,
        company_id: UUID,
        lines: Iterable[CompanyLedgerLineRaw],
    ) -> list[CompanyValueTypeFinancials]:

        groups: dict[str | None, CompanyValueTypeFinancials] = {}

        for line in lines:
            period = cls.classify(line=line, company_id=company_id)
            if period is None:
                continue

            current = groups.get(line.value_type_id)
            groups[line.value_type_id] = CompanyValueTypeFinancials(
                value_type_id=line.value_type_id,
                code=line.value_type_code,
                name=line.value_type_name,
                is_fixed=cls.is_fixed(line=line, company_id=company_id),
                financials=(current.financials if current else EMPTY) + period,
            )

        return list(groups.values())

    # =====================================================
    # LINE
    # =====================================================

    @classmethod
    def classify(
        cls,
        *,
        line: CompanyLedgerLineRaw,
        company_id: UUID,
    ) -> CompanyPeriodFinancials | None:

        pillars = Pillars.of(cls.amount(line))

        if cls.is_fixed(line=line, company_id=company_id):
            return CompanyPeriodFinancials(cost=pillars, fixed=pillars)

        company = str(company_id)

        if str(line.seller_id) == company:
            return CompanyPeriodFinancials(revenue=pillars)

        if str(line.buyer_id) == company:
            return CompanyPeriodFinancials(cost=pillars)

        return None

    @staticmethod
    def is_fixed(*, line: CompanyLedgerLineRaw, company_id: UUID) -> bool:
        if str(line.seller_id) == str(company_id):
            # sprzedaż firmy nigdy nie jest jej kosztem stałym
            return False
        if line.direction == ValueDirection.FIXED.value:
            return True
        # LEGACY: koszty stałe księgowane na kontrakcie systemowym firmy
        return (
            line.contract_type == "system"
            and str(line.contract_owner_id) == str(company_id)
        )

    @staticmethod
    def amount(line: CompanyLedgerLineRaw) -> Amount:
        return Amount.from_input(
            value=Decimal(line.amount_value),
            input_type=AmountInputType(line.amount_input_type),
            vat_rate=VatRate(Decimal(line.vat_rate)),
            tax_treatment=TaxTreatment(line.tax_treatment),
        )
