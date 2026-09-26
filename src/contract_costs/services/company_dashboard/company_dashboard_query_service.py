from datetime import datetime

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.company_dashboard.dto.company_dashboard_data import CompanyDashboardData
from contract_costs.services.company_dashboard.dto.company_dashboard_month import CompanyDashboardMonth
from contract_costs.services.company_dashboard.dto.company_dashboard_query import (
    CompanyDashboardQuery,
)
from contract_costs.services.company_dashboard.financials.company_financials_calculator import (
    MONTH_NAMES,
    CompanyFinancialsCalculator,
    period_range,
)
from contract_costs.unit_of_work import UnitOfWork


class CompanyDashboardQueryService(
    ActionHandler[CompanyDashboardQuery, CompanyDashboardData]
):

    def execute(
        self,
        *,
        action: CompanyDashboardQuery,
        uow: UnitOfWork,
    ) -> CompanyDashboardData:

        company_repo = uow.companies
        dashboard_repo = uow.company_dashboard

        company = self._resolve_company(
            action=action,
            company_repo=company_repo,
        )

        owners = company_repo.get_owners(
            organization_id=action.organization_id
        )

        year = action.year or datetime.now().year
        start, end = period_range(year, None)

        lines = dashboard_repo.fetch_company_lines(
            organization_id=action.organization_id,
            company_id=company.id,
            start=start,
            end=end,
        )
        financials = CompanyFinancialsCalculator.calculate(
            year=year,
            company_id=company.id,
            lines=lines,
        )

        months = [
            CompanyDashboardMonth(month=month, label=MONTH_NAMES[month], period=period)
            for month, period in sorted(financials.months.items(), reverse=True)
        ]

        return CompanyDashboardData(
            owner_companies=owners,
            selected_company_id=company.id,
            year=year,
            financials=financials,
            months=months,
        )

    @staticmethod
    def _resolve_company(*, action, company_repo):

        if action.company_id:
            company = company_repo.get(
                organization_id=action.organization_id,
                company_id=action.company_id,
            )

            if not company:
                raise RuntimeError("Company not found")

            return company

        if action.tax_number:
            company = company_repo.get_by_tax_number(
                organization_id=action.organization_id,
                tax_number=action.tax_number,
            )

            if not company:
                raise RuntimeError("Company not found")

            return company

        owners = company_repo.get_owners(
            organization_id=action.organization_id
        )

        if not owners:
            raise RuntimeError("No OWN companies configured")

        return owners[0]
