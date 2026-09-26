from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from contract_costs.common.ids import new_uuid
from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.document import DocumentStatus
from contract_costs.model.financial_record import PaymentStatus
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.inmemory.company_dashboard.company_dashboard_repository import (
    InMemoryCompanyDashboardRepository,
)
from contract_costs.services.contracts.financials.contract_financials import ContractIndicators, IndicatorLevel
from contract_costs.services.dashboard import dashboard_query_service
from contract_costs.services.dashboard.dashboard_query_service import DashboardQueryService
from contract_costs.services.dashboard.dto.dashboard_query import DashboardQuery
from tests.unit.services.company.test_company_financials_calculator import CLIENT, SUPPLIER, YEAR, _line

ORG = new_uuid()
USER = new_uuid()
A = new_uuid()
B = new_uuid()


def _owners(*extra):
    return [
        SimpleNamespace(id=A, name="Firma A", is_active=True),
        SimpleNamespace(id=B, name="Firma B", is_active=True),
        *extra,
    ]


class _Records:
    def __init__(self, by_direction):
        self._by_direction = by_direction

    def count_for_review(self, *, organization_id, query):
        return 7 if query.statuses else 0

    def list_for_review(self, *, organization_id, query):
        directions = query.direction if isinstance(query.direction, list) else [query.direction]
        return [r for d in directions for r in self._by_direction.get(d, [])]


class _Lines:
    def __init__(self, lines):
        self._lines = lines

    def list_by_financial_record_ids(self, *, organization_id, financial_records_ids):
        return [l for l in self._lines if l.financial_record_id in financial_records_ids]


class _Payments:
    def __init__(self, payments):
        self._payments = payments

    def list_by_financial_record(self, *, organization_id, financial_record_id):
        return [p for p in self._payments if p.financial_record_id == financial_record_id]


def _uow(lines=(), owners=None, unpaid=None, record_lines=(), payments=(), documents=()):
    return SimpleNamespace(
        companies=SimpleNamespace(get_owners=lambda organization_id: owners or _owners()),
        company_dashboard=InMemoryCompanyDashboardRepository([(ORG, l) for l in lines]),
        financial_records=_Records(unpaid or {}),
        financial_record_lines=_Lines(list(record_lines)),
        financial_record_payments=_Payments(list(payments)),
        contracts=SimpleNamespace(list_contracts=lambda **kwargs: []),
        value_types=SimpleNamespace(list_all=lambda **kwargs: []),
        documents=SimpleNamespace(
            list_filtered=lambda *, organization_id, document_status: [
                d for d in documents if d.status == document_status
            ],
        ),
    )


def _run(uow, today=date(YEAR, 4, 15)):
    return DashboardQueryService().execute(
        action=DashboardQuery(organization_id=ORG, actor_user_id=USER, today=today),
        uow=uow,
    )


def test_cards_count_internal_but_group_eliminates_it():
    lines = [
        _line(buyer=CLIENT, seller=A, value="1000.00", direction="REVENUE"),
        _line(buyer=B, seller=A, value="200.00", direction="INTERNAL"),
        _line(buyer=B, seller=SUPPLIER, value="300.00", direction="COST"),
    ]

    data = _run(_uow(lines))

    card_a, card_b = data.companies
    assert card_a.periods.year.revenue.net == Decimal("1200.00")
    assert card_b.periods.year.cost.net == Decimal("500.00")

    group = data.group.year
    assert group.revenue.net == Decimal("1000.00")
    assert group.cost.net == Decimal("300.00")
    assert group.result_net == card_a.periods.year.result_net + card_b.periods.year.result_net


def test_last_month_is_previous_full_month():
    lines = [
        _line(buyer=CLIENT, seller=A, value="100.00", direction="REVENUE", month=3),
        _line(buyer=CLIENT, seller=A, value="50.00", direction="REVENUE", month=4),
    ]

    data = _run(_uow(lines), today=date(YEAR, 4, 15))

    assert (data.last_month_year, data.last_month) == (YEAR, 3)
    assert data.companies[0].periods.last_month.revenue.net == Decimal("100.00")
    assert data.companies[0].periods.year.revenue.net == Decimal("150.00")


def test_january_uses_december_of_previous_year():
    data = _run(_uow(), today=date(YEAR, 1, 5))

    assert (data.last_month_year, data.last_month) == (YEAR - 1, 12)


def test_unapproved_records_are_counted_not_summed():
    lines = [
        _line(buyer=CLIENT, seller=A, value="100.00", direction="REVENUE"),
        _line(buyer=CLIENT, seller=A, value="999.00", direction="REVENUE", status="new_revenue"),
    ]

    card = _run(_uow(lines)).companies[0]

    assert card.periods.year.revenue.net == Decimal("100.00")
    assert card.unapproved_record_count == 1


def test_inactive_owner_is_skipped():
    owners = _owners(SimpleNamespace(id=new_uuid(), name="Stara", is_active=False))

    data = _run(_uow(owners=owners))

    assert [c.name for c in data.companies] == ["Firma A", "Firma B"]


def _record_line(record_id, value, tax="tax_deductible"):
    return SimpleNamespace(
        financial_record_id=record_id,
        amount=Amount.from_input(
            value=Decimal(value),
            input_type=AmountInputType("net"),
            vat_rate=VatRate(Decimal("0.23")),
            tax_treatment=TaxTreatment(tax),
        ),
    )


def test_unpaid_sums_remaining_gross_payable():
    unpaid_record = SimpleNamespace(id=new_uuid(), payment_status=PaymentStatus.UNPAID)
    partial_record = SimpleNamespace(id=new_uuid(), payment_status=PaymentStatus.PARTIALLY_PAID)
    revenue_record = SimpleNamespace(id=new_uuid(), payment_status=PaymentStatus.UNPAID)

    uow = _uow(
        unpaid={
            ValueDirection.COST: [unpaid_record],
            ValueDirection.FIXED: [partial_record],
            ValueDirection.REVENUE: [revenue_record],
        },
        record_lines=[
            _record_line(unpaid_record.id, "100.00"),                     # 123 brutto
            _record_line(unpaid_record.id, "50.00", tax="non_cash_cost"),  # nic do zapłaty
            _record_line(partial_record.id, "200.00"),                    # 246 brutto
            _record_line(revenue_record.id, "1000.00"),                   # 1230 brutto
        ],
        payments=[SimpleNamespace(financial_record_id=partial_record.id, amount=Decimal("46.00"))],
    )

    data = _run(uow)

    assert (data.unpaid_costs.count, data.unpaid_costs.amount) == (2, Decimal("323.00"))
    assert (data.unpaid_revenue.count, data.unpaid_revenue.amount) == (1, Decimal("1230.00"))
    assert (data.unpaid_internal.count, data.unpaid_internal.amount) == (0, Decimal("0.00"))


def test_counts_documents_and_records_to_assign():
    documents = [
        SimpleNamespace(status=DocumentStatus.READY),
        SimpleNamespace(status=DocumentStatus.READY),
        SimpleNamespace(status=DocumentStatus.APPLIED),
    ]

    data = _run(_uow(documents=documents))

    assert data.documents_to_assign == 2
    assert data.records_to_assign == 7


def _indicators(cost=None, schedule=None, billing=None, stale=None):
    return ContractIndicators(
        cost=cost, schedule=schedule, billing=billing,
        time_progress=None, last_progress_date=None, progress_stale=stale,
    )


G, Y, R = IndicatorLevel.GREEN, IndicatorLevel.YELLOW, IndicatorLevel.RED


def test_contract_level_is_worst_indicator():
    level = DashboardQueryService.contract_level
    assert level(_indicators(G, G, G)) == G
    assert level(_indicators(None, None, None)) == G
    assert level(_indicators(G, Y, G)) == Y
    assert level(_indicators(G, G, G, stale=True)) == Y
    assert level(_indicators(Y, R, G)) == R


def test_contracts_counts_all_and_lists_only_problems(monkeypatch):
    def contract(code, indicators, is_active=True):
        return SimpleNamespace(
            contract_id=new_uuid(), code=code, name=code, is_active=is_active,
            financials=SimpleNamespace(indicators=indicators),
        )

    contracts = [
        contract("K3", _indicators(G, Y, G)),
        contract("K1", _indicators(G, G, G)),
        contract("K2", _indicators(R, G, G)),
        contract("K4", _indicators(R, R, R), is_active=False),
    ]
    monkeypatch.setattr(
        dashboard_query_service.ListContractsQueryService, "execute",
        lambda self, *, action, uow: contracts,
    )

    result = _run(_uow()).contracts

    assert (result.active, result.ok, result.watch, result.at_risk) == (3, 1, 1, 1)
    assert [c.code for c in result.flagged] == ["K2", "K3"]
