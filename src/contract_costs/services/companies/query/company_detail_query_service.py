from collections import defaultdict

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.companies.query.dto.company_detail_dto import CompanyDetailDTO
from contract_costs.services.companies.query.dto.company_detail_query import CompanyDetailQuery
from contract_costs.services.companies.query.dto.company_year_dto import CounterpartyYearDTO
from contract_costs.services.company_dashboard.financials.company_financials import CompanyPeriodFinancials
from contract_costs.services.company_dashboard.financials.company_financials_calculator import (
    CompanyFinancialsCalculator,
)
from contract_costs.unit_of_work import UnitOfWork

YEARS_SHOWN = 5


class CompanyDetailQueryService(
    ActionHandler[CompanyDetailQuery, CompanyDetailDTO]
):
    """
    Współpraca z kontrahentem z perspektywy firm own.

    Kwoty liczy CompanyFinancialsCalculator (te same reguły co finanse firmy),
    tylko z rekordów zatwierdzonych. Liczniki faktur i nieopłaconych obejmują
    wszystkie rekordy — tak jak lista faktur pod spodem.
    """

    def execute(
        self,
        *,
        action: CompanyDetailQuery,
        uow: UnitOfWork,
    ) -> CompanyDetailDTO:

        company = uow.companies.get(
            organization_id=action.organization_id,
            company_id=action.company_id,
        )

        if not company:
            raise ValueError("Company not found")

        lines = uow.company_dashboard.fetch_counterparty_lines(
            organization_id=action.organization_id,
            counterparty_id=action.company_id,
            owner_company_id=action.owner_company_id,
        )

        total = CompanyPeriodFinancials()
        invoice_ids: set[str] = set()
        unpaid_invoice_ids: set[str] = set()
        unapproved_ids: set[str] = set()
        last_invoice_date = None

        years: dict[int, CompanyPeriodFinancials] = defaultdict(CompanyPeriodFinancials)
        year_invoice_ids: dict[int, set[str]] = defaultdict(set)

        for line in lines:
            record_id = str(line.record_id)
            invoice_ids.add(record_id)

            if line.payment_status != "paid":
                unpaid_invoice_ids.add(record_id)

            if line.record_date is None:
                continue

            if last_invoice_date is None or line.record_date > last_invoice_date:
                last_invoice_date = line.record_date

            year = line.record_date.year
            year_invoice_ids[year].add(record_id)

            if not CompanyFinancialsCalculator.is_approved(line):
                unapproved_ids.add(record_id)
                continue

            period = CompanyFinancialsCalculator.classify_against(
                line=line,
                counterparty_id=action.company_id,
            )
            if period is None:
                continue

            total += period
            years[year] += period

        years_dto = [
            CounterpartyYearDTO(
                year=year,
                invoice_count=len(year_invoice_ids[year]),
                financials=years.get(year, CompanyPeriodFinancials()),
            )
            for year in sorted(year_invoice_ids, reverse=True)[:YEARS_SHOWN]
        ]

        return CompanyDetailDTO(
            company_id=company.id,
            name=company.name,
            tax_number=company.tax_number,
            role=company.role.value,
            is_active=company.is_active,

            invoice_count=len(invoice_ids),

            financials=total,

            unpaid_invoices=len(unpaid_invoice_ids),
            last_invoice_date=last_invoice_date,
            unapproved_record_count=len(unapproved_ids),

            years=years_dto,
        )
