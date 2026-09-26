from decimal import Decimal
from types import SimpleNamespace

from contract_costs.common.ids import new_uuid
from contract_costs.repository.inmemory.company_dashboard.company_dashboard_repository import (
    InMemoryCompanyDashboardRepository,
)
from contract_costs.services.companies.query.company_detail_query_service import CompanyDetailQueryService
from contract_costs.services.companies.query.dto.company_detail_query import CompanyDetailQuery
from tests.unit.services.company.test_company_financials_calculator import (
    COMPANY,
    OTHER_OWN,
    SUPPLIER,
    _line,
)

ORG = new_uuid()


class _Companies:
    def get(self, *, organization_id, company_id):
        return SimpleNamespace(
            id=company_id, name="Kontrahent", tax_number="123",
            role=SimpleNamespace(value="SUPPLIER"), is_active=True,
        )


def _detail(lines, *, counterparty=SUPPLIER, owner=None):
    uow = SimpleNamespace(
        companies=_Companies(),
        company_dashboard=InMemoryCompanyDashboardRepository([(ORG, line) for line in lines]),
    )
    return CompanyDetailQueryService().execute(
        action=CompanyDetailQuery(
            organization_id=ORG, actor_user_id=new_uuid(),
            company_id=counterparty, owner_company_id=owner,
        ),
        uow=uow,
    )


def test_purchase_from_supplier_is_our_cost_in_amount_pillars():
    detail = _detail([
        _line(buyer=COMPANY, seller=SUPPLIER, value="123.00", input_type="gross"),
        _line(buyer=COMPANY, seller=SUPPLIER, value="40.00", tax="non_deductible"),
    ])

    assert detail.financials.cost.net == Decimal("100.00")
    assert detail.financials.cost.non_tax == Decimal("40.00")
    assert detail.financials.cost.cashflow == Decimal("140.00")
    assert detail.financials.revenue.cashflow == Decimal("0")
    assert detail.financials.result_cashflow == Decimal("-140.00")


def test_sale_to_client_is_our_revenue():
    detail = _detail(
        [_line(buyer=SUPPLIER, seller=COMPANY, value="500.00", direction="REVENUE")],
    )

    assert detail.financials.revenue.cashflow == Decimal("500.00")
    assert detail.years[0].financials.revenue.net == Decimal("500.00")


def test_unapproved_records_are_counted_but_not_summed():
    detail = _detail([
        _line(buyer=COMPANY, seller=SUPPLIER, value="100.00"),
        _line(buyer=COMPANY, seller=SUPPLIER, value="900.00", status="new_cost"),
    ])

    assert detail.invoice_count == 2
    assert detail.unapproved_record_count == 1
    assert detail.financials.cost.cashflow == Decimal("100.00")
    assert detail.years[0].invoice_count == 2


def test_owner_filter_limits_to_one_own_company():
    detail = _detail(
        [
            _line(buyer=COMPANY, seller=SUPPLIER, value="100.00"),
            _line(buyer=OTHER_OWN, seller=SUPPLIER, value="300.00"),
        ],
        owner=OTHER_OWN,
    )

    assert detail.financials.cost.cashflow == Decimal("300.00")
