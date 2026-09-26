from dataclasses import dataclass

from contract_costs.services.company_dashboard.financials.company_financials import CompanyPeriodFinancials


@dataclass
class CounterpartyYearDTO:
    year: int
    invoice_count: int
    # z naszej perspektywy: przychód = sprzedaż do kontrahenta, koszt = zakup od niego
    financials: CompanyPeriodFinancials
