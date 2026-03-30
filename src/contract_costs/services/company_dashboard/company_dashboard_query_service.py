from datetime import datetime

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.company_dashboard.dto.company_dashboard_data import (
    CompanyDashboardData,
    CompanyDashboardMonth,
)
from contract_costs.services.company_dashboard.dto.company_dashboard_query import (
    CompanyDashboardQuery,
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

        raw = dashboard_repo.fetch_dashboard_data(
            organization_id=action.organization_id,
            company_id=company.id,
            year=year,
        )

        # ===============================
        # YEAR TOTALS
        # ===============================

        year_revenue = raw.year_revenue
        year_costs = raw.year_costs

        year_profit = year_revenue - year_costs
        year_cashflow = (
                year_profit
                - raw.year_non_deductible
                - raw.year_fixed_costs
        )

        # ===============================
        # MONTHS
        # ===============================

        months: list[CompanyDashboardMonth] = []

        for row in raw.months:

            revenue = row.revenue
            costs = row.costs

            profit = revenue - costs
            cashflow = (
                    profit
                    - row.non_deductible
                    - row.fixed_costs
            )

            months.append(
                CompanyDashboardMonth(
                    label=row.label,
                    revenue=revenue,
                    costs=costs,
                    profit=profit,
                    non_deductible=row.non_deductible,
                    cashflow=cashflow,
                    fixed_costs=row.fixed_costs,
                    month=row.month,
                )
            )

        current_month = months[0] if months else None
        previous_months = months[1:] if len(months) > 1 else []

        # ===============================
        # RETURN
        # ===============================

        return CompanyDashboardData(

            owner_companies=owners,
            selected_company_id=company.id,

            year=year,

            year_revenue=year_revenue,
            year_costs=year_costs,
            year_profit=year_profit,

            year_non_deductible=raw.year_non_deductible,
            year_cashflow=year_cashflow,
            year_fixed_costs=raw.year_fixed_costs,

            current_month=current_month,
            previous_months=previous_months,
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