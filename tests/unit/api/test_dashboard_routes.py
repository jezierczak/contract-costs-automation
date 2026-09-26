from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.templating import Jinja2Templates

from api import template_filters
from api.routers import dashboard
from contract_costs.services.dashboard.dto.dashboard_data import (
    DashboardContracts,
    DashboardData,
    DashboardPeriods,
    UnpaidSummary,
)
from contract_costs.services.company_dashboard.financials.company_financials import CompanyPeriodFinancials

TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "src" / "api" / "templates"


class _FakeUow:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    companies = SimpleNamespace(exists_owner=lambda organization_id: True)


def _empty_dashboard(*, action, handler):
    empty = DashboardPeriods(year=CompanyPeriodFinancials(), last_month=CompanyPeriodFinancials())
    unpaid = UnpaidSummary(count=0, amount=0)
    return DashboardData(
        year=2026, last_month_year=2026, last_month=3, companies=[], group=empty,
        unpaid_costs=unpaid, unpaid_revenue=unpaid, unpaid_internal=unpaid,
        documents_to_assign=0, records_to_assign=0,
        contracts=DashboardContracts(active=0, ok=0, watch=0, at_risk=0, flagged=[]),
    )


def _client() -> TestClient:
    app = FastAPI()
    app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    template_filters.register(app.state.templates.env)
    app.state.services = SimpleNamespace(
        uow=_FakeUow(),
        action_bus=SimpleNamespace(execute=_empty_dashboard),
        dashboard_query_service=None,
    )

    @app.middleware("http")
    async def fake_ctx(request, call_next):
        request.state.ctx = SimpleNamespace(
            user_id=uuid4(),
            organization_id=uuid4(),
            organization=SimpleNamespace(name="Org", code="ORG"),
            user=SimpleNamespace(login="tester", last_login_at=None),
            membership=SimpleNamespace(role=SimpleNamespace(value="owner")),
        )
        return await call_next(request)

    app.include_router(dashboard.router)
    return TestClient(app)


def test_menu_click_returns_only_content():
    response = _client().get("/dashboard", headers={"HX-Request": "true"})

    assert response.status_code == 200
    assert "Pobierz wszystko z KSeF" in response.text
    assert "<html" not in response.text.lower()


def test_page_refresh_on_dashboard_returns_full_layout():
    response = _client().get("/dashboard")

    assert response.status_code == 200
    assert "<html" in response.text.lower()
    assert "Pobierz wszystko z KSeF" in response.text


def test_dashboard_shows_overview_sections():
    response = _client().get("/dashboard", headers={"HX-Request": "true"})

    assert "Do przypisania" in response.text
    assert "Niezapłacone faktury" in response.text
    assert "Aktywne kontrakty" in response.text
    assert "Grupa – wszystkie firmy razem" in response.text
