from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.templating import Jinja2Templates

from api.routers import dashboard

TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "src" / "api" / "templates"


class _FakeUow:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    companies = SimpleNamespace(exists_owner=lambda organization_id: True)


def _client() -> TestClient:
    app = FastAPI()
    app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    app.state.services = SimpleNamespace(uow=_FakeUow())

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
