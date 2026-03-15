from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.services.companies.query.dto.company_year_dto import CounterpartyYearDTO


@dataclass
class CompanyDetailDTO:

    company_id: UUID
    name: str
    tax_number: str
    role: str
    is_active: bool

    invoice_count: int

    revenue: Decimal
    costs: Decimal
    balance: Decimal

    unpaid_invoices: int
    last_invoice_date: date | None

    years: list["CounterpartyYearDTO"]