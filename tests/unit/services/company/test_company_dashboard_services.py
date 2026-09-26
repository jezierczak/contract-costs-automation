from decimal import Decimal
from types import SimpleNamespace

from contract_costs.common.ids import new_uuid
from contract_costs.repository.inmemory.company_dashboard.company_dashboard_repository import (
    InMemoryCompanyDashboardRepository,
)
from contract_costs.services.company_dashboard.company_fixed_costs_query_service import (
    CompanyFixedCostsQueryService,
)
from contract_costs.services.company_dashboard.company_month_breakdown_query_service import (
    CompanyMonthBreakdownQueryService,
)
from contract_costs.services.company_dashboard.dto.company_fixerd_costs_query import CompanyFixedCostsQuery
from contract_costs.services.company_dashboard.dto.company_month_breakdown_query import CompanyBreakdownQuery
from tests.unit.services.company.test_company_financials_calculator import (
    CLIENT,
    COMPANY,
    SUPPLIER,
    YEAR,
    _line,
)

ORG = new_uuid()
LINES = [
    _line(buyer=CLIENT, seller=COMPANY, value="1000.00", direction="REVENUE", value_type_id="vt-rev"),
    _line(buyer=COMPANY, seller=SUPPLIER, value="300.00", value_type_id="vt-mat"),
    _line(buyer=COMPANY, seller=SUPPLIER, value="100.00", direction="FIXED", tax="non_deductible", value_type_id="vt-zus"),
    _line(buyer=COMPANY, seller=SUPPLIER, value="999.00", direction="FIXED", status="new_cost", value_type_id="vt-zus"),
    _line(buyer=COMPANY, seller=SUPPLIER, value="50.00", direction="FIXED", month=4, value_type_id="vt-bank"),
]


def _uow():
    return SimpleNamespace(
        company_dashboard=InMemoryCompanyDashboardRepository([(ORG, line) for line in LINES])
    )


def test_breakdown_splits_costs_and_revenues_by_value_type():
    data = CompanyMonthBreakdownQueryService().execute(
        action=CompanyBreakdownQuery(
            organization_id=ORG, actor_user_id=new_uuid(), company_id=COMPANY, year=YEAR, month=3,
        ),
        uow=_uow(),
    )

    assert [(i.code, i.pillars.cashflow, i.is_fixed) for i in data.costs] == [
        ("VT-MAT", Decimal("300.00"), False),
        ("VT-ZUS", Decimal("100.00"), True),
    ]
    assert data.cost_total.cashflow == Decimal("400.00")
    assert data.revenue_total.cashflow == Decimal("1000.00")
    assert data.costs[0].share == Decimal("0.75")


def test_fixed_costs_show_only_approved_fixed_lines_of_period():
    data = CompanyFixedCostsQueryService().execute(
        action=CompanyFixedCostsQuery(
            organization_id=ORG, actor_user_id=new_uuid(), company_id=COMPANY, year=YEAR, month=3,
        ),
        uow=_uow(),
    )

    assert [vt.value_type_code for vt in data.value_types] == ["VT-ZUS"]
    assert data.total.cashflow == Decimal("100.00")
    assert data.total.net == Decimal("0.00")
