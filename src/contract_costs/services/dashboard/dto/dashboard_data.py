from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from contract_costs.services.company_dashboard.financials.company_financials import CompanyPeriodFinancials


@dataclass(frozen=True)
class DashboardPeriods:
    """Wynik za bieżący rok i za poprzedni (pełny) miesiąc."""
    year: CompanyPeriodFinancials
    last_month: CompanyPeriodFinancials


@dataclass(frozen=True)
class DashboardCompanyCard:
    company_id: UUID
    name: str
    periods: DashboardPeriods
    unapproved_record_count: int


@dataclass(frozen=True)
class UnpaidSummary:
    """Faktury niezapłacone w całości: liczba i suma brutto, która zostało do zapłaty (payable − wpłaty)."""
    count: int
    amount: Decimal


@dataclass(frozen=True)
class DashboardData:
    year: int
    last_month_year: int
    last_month: int
    companies: list[DashboardCompanyCard]
    # organizacja jako całość: INTERNAL między firmami own się znosi
    group: DashboardPeriods
    unpaid_costs: UnpaidSummary
    unpaid_revenue: UnpaidSummary
    unpaid_internal: UnpaidSummary
    # do przypisania: dokumenty READY (czekają na ekran dopasowania) i rekordy z widoku „Do przypisania”
    documents_to_assign: int
    records_to_assign: int
