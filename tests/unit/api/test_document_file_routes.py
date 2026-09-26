from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from starlette.templating import Jinja2Templates

from api.dependencies import get_services
from api.routers import documents
from contract_costs.services.documents.query.dto.document_file_dto import DocumentFileDto
from tests.unit.ksef.test_invoice_visualisation import FA3_INVOICE

API_DIR = Path(__file__).resolve().parents[3] / "src" / "api"


def _client(file_path: Path, ksef_number: str | None = None) -> TestClient:
    app = FastAPI()
    app.state.templates = Jinja2Templates(directory=str(API_DIR / "templates"))
    app.mount("/static", StaticFiles(directory=str(API_DIR / "static")), name="static")

    @app.middleware("http")
    async def fake_ctx(request, call_next):
        request.state.ctx = SimpleNamespace(user_id=uuid4(), organization_id=uuid4())
        return await call_next(request)

    services = SimpleNamespace(
        action_bus=SimpleNamespace(execute=lambda **kwargs: DocumentFileDto(file_path=str(file_path), ksef_number=ksef_number)),
        get_document_file_service=object(),
    )
    app.dependency_overrides[get_services] = lambda: services
    app.include_router(documents.router)
    return TestClient(app)


def _invoice(tmp_path: Path) -> Path:
    path = tmp_path / "FV_7_2026.xml"
    path.write_text(FA3_INVOICE, encoding="utf-8")
    return path


def test_xml_preview_is_the_mf_pdf_generator_page(tmp_path):
    client = _client(_invoice(tmp_path))

    response = client.get(f"/documents/{uuid4()}/file")

    assert response.status_code == 200
    assert "ksef-fe-invoice-converter.umd.js" in response.text
    assert '"FV_7_2026.pdf"' in response.text
    script = client.get("/static/vendor/ksef-pdf-generator/ksef-fe-invoice-converter.umd.js")
    assert script.status_code == 200


def test_raw_and_mf_views(tmp_path):
    client = _client(_invoice(tmp_path))

    raw = client.get(f"/documents/{uuid4()}/file?raw=1")
    mf = client.get(f"/documents/{uuid4()}/file?mf=1")

    assert "<Faktura" in raw.text
    assert "FV/7/2026" in mf.text and "window.print()" in mf.text


def test_missing_file_returns_404(tmp_path):
    response = _client(tmp_path / "gone.xml").get(f"/documents/{uuid4()}/file")

    assert response.status_code == 404
    assert "Brak pliku" in response.text


def test_ksef_invoice_preview_gets_ksef_number_and_qr_code(tmp_path):
    client = _client(_invoice(tmp_path), ksef_number="2222222222-20260915-0100001AF629-AF")

    response = client.get(f"/documents/{uuid4()}/file")

    assert '"2222222222-20260915-0100001AF629-AF"' in response.text
    assert "https://qr.ksef.mf.gov.pl/invoice/2222222222/15-09-2026/" in response.text


def test_non_ksef_invoice_preview_has_no_qr_code(tmp_path):
    response = _client(_invoice(tmp_path)).get(f"/documents/{uuid4()}/file")

    assert "qr.ksef.mf.gov.pl" not in response.text

