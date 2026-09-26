from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.repository.company_dashboard.company_dashboard_repository import (
    CompanyDashboardRepository,
)
from contract_costs.repository.company_dashboard.dto.company_dashboard_raw_data import (
    CompanyDashboardRawData,
)
from contract_costs.repository.company_dashboard.dto.company_fixed_cost_raw import CompanyFixedCostRaw
from contract_costs.repository.company_dashboard.dto.company_ledger_line_raw import CompanyLedgerLineRaw
from contract_costs.repository.company_dashboard.dto.company_month_breakdown_raw import CompanyMonthBreakdownRaw
from contract_costs.repository.company_dashboard.dto.counterparty_ledger_line_raw import CounterpartyLedgerLineRaw


class InMemoryCompanyDashboardRepository(CompanyDashboardRepository):

    def __init__(self, ledger_rows: list[dict] | None = None) -> None:
        """
        ledger_rows = dane odpowiadające financial_ledger view
        """
        self._rows = ledger_rows or []

    def fetch_dashboard_data(
        self,
        *,
        organization_id: UUID,
        company_id: UUID,
        year:int
    ) -> CompanyDashboardRawData:

        today = date.today()
        current_year = year
        current_month = today.month

        last_month_date = (
            date(today.year - 1, 12, 1)
            if today.month == 1
            else date(today.year, today.month - 1, 1)
        )

        last_month = last_month_date.month
        last_month_year = last_month_date.year

        revenue_ytd = Decimal("0")
        cost_tax_ytd = Decimal("0")
        cost_non_tax_ytd = Decimal("0")

        revenue_this_month = Decimal("0")
        cost_tax_this_month = Decimal("0")
        cost_non_tax_this_month = Decimal("0")

        revenue_last_month = Decimal("0")
        cost_tax_last_month = Decimal("0")
        cost_non_tax_last_month = Decimal("0")

        contract_costs_ytd = Decimal("0")
        fixed_costs_ytd = Decimal("0")

        for r in self._rows:

            if r["organization_id"] != organization_id:
                continue

            year = r["record_year"]
            month = r["record_month"]
            amount = Decimal(r["amount_value"])
            direction = r["direction"]
            tax = r["tax_treatment"]

            is_revenue = direction == "REVENUE" and r["seller_id"] == company_id
            is_cost = direction == "COST" and r["buyer_id"] == company_id

            # YTD
            if year == current_year:

                if is_revenue:
                    revenue_ytd += amount

                if is_cost:
                    if tax == "tax_deductible":
                        cost_tax_ytd += amount
                    else:
                        cost_non_tax_ytd += amount

                    if r["contract_id"]:
                        contract_costs_ytd += amount
                    else:
                        fixed_costs_ytd += amount

            # CURRENT MONTH
            if year == current_year and month == current_month:

                if is_revenue:
                    revenue_this_month += amount

                if is_cost:
                    if tax == "tax_deductible":
                        cost_tax_this_month += amount
                    else:
                        cost_non_tax_this_month += amount

            # LAST MONTH
            if year == last_month_year and month == last_month:

                if is_revenue:
                    revenue_last_month += amount

                if is_cost:
                    if tax == "tax_deductible":
                        cost_tax_last_month += amount
                    else:
                        cost_non_tax_last_month += amount

        return CompanyDashboardRawData(
            revenue_ytd=revenue_ytd,
            costs_tax_deductible_ytd=cost_tax_ytd,
            costs_non_deductible_ytd=cost_non_tax_ytd,

            revenue_this_month=revenue_this_month,
            costs_tax_deductible_this_month=cost_tax_this_month,
            costs_non_deductible_this_month=cost_non_tax_this_month,

            revenue_last_month=revenue_last_month,
            costs_tax_deductible_last_month=cost_tax_last_month,
            costs_non_deductible_last_month=cost_non_tax_last_month,

            contract_costs_ytd=contract_costs_ytd,
            fixed_costs_ytd=fixed_costs_ytd,
        )

    # =====================================================
    # STUBS
    # (TODO: to nieaktualna implementacja względem MySQL –
    #  wymaga osobnej pracy, poza zakresem partial payments;
    #  na razie tylko odblokowują instancjonowanie InMemoryUnitOfWork)
    # =====================================================

    def fetch_company_lines(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            start: date,
            end: date,
    ) -> list[CompanyLedgerLineRaw]:
        return []

    def fetch_month_breakdown(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            year: int,
            month: int,
    ) -> list[CompanyMonthBreakdownRaw]:
        return []

    def fetch_fixed_costs(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            year: int,
            month: int | None,
    ) -> list[CompanyFixedCostRaw]:
        return []

    def fetch_counterparty_lines(
            self,
            *,
            organization_id: UUID,
            counterparty_id: UUID,
            owner_company_id: UUID | None,
    ) -> list[CounterpartyLedgerLineRaw]:
        return []