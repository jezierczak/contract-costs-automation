from dataclasses import dataclass
from datetime import date
from uuid import UUID

from contract_costs.services.companies.query.dto.company_year_dto import CounterpartyYearDTO
from contract_costs.services.company_dashboard.financials.company_financials import CompanyPeriodFinancials


@dataclass
class CompanyDetailDTO:

    company_id: UUID
    name: str
    tax_number: str
    role: str
    is_active: bool

    invoice_count: int

    # tylko rekordy zatwierdzone — trzy filary z Amount
    financials: CompanyPeriodFinancials

    unpaid_invoices: int
    last_invoice_date: date | None

    # rekordy jeszcze niezatwierdzone — nie wchodzą do kwot
    unapproved_record_count: int

    years: list[CounterpartyYearDTO]
