from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.templating import Jinja2Templates

from api.dependencies import get_services
from api.routers import companies
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.builders.company_builder import CompanyBuilder

API_DIR = Path(__file__).resolve().parents[3] / "src" / "api"
ORG = uuid4()


def _client(uow) -> TestClient:
    app = FastAPI()
    app.state.templates = Jinja2Templates(directory=str(API_DIR / "templates"))

    @app.middleware("http")
    async def fake_ctx(request, call_next):
        request.state.ctx = SimpleNamespace(user_id=uuid4(), organization_id=ORG)
        return await call_next(request)

    app.dependency_overrides[get_services] = lambda: SimpleNamespace(uow=uow)
    app.include_router(companies.router)
    return TestClient(app)


def test_next_identifier_returns_input_with_next_number():
    uow = InMemoryUnitOfWork()
    uow.companies.add(CompanyBuilder().with_organization_id(ORG).with_tax_number("OTH-000004").build())

    response = _client(uow).get("/companies/next-identifier")

    assert response.status_code == 200
    assert 'id="company-tax-number"' in response.text
    assert 'value="OTH-000005"' in response.text


def test_new_company_form_has_generate_button():
    response = _client(InMemoryUnitOfWork()).get("/companies/new")

    assert response.status_code == 200
    assert "Generuj numer" in response.text
    assert 'hx-get="/companies/next-identifier"' in response.text
