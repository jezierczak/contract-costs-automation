import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.templating import Jinja2Templates

from api.dependencies import get_services
from api.routers import documents
from contract_costs.services.documents.apply.apply_document_service import SellerMismatchError
from contract_costs.services.documents.query.dto.document_match_dto import (
    CompanySummaryDto,
    DocumentMatchDto,
    DocumentPartyDto,
    MatchCandidateDto,
)

API_DIR = Path(__file__).resolve().parents[3] / "src" / "api"
DOC_ID = uuid4()


def _dto():
    seller_company = CompanySummaryDto(id=uuid4(), name="DOMBUD", tax_number="6431668510", to_verify=False)
    return DocumentMatchDto(
        document_id=DOC_ID,
        document_source="pdf",
        document_type="invoice",
        document_number="FPF/982/2026",
        seller_nip="6431668510",
        file_path="raw/x.pdf",
        confidence_score=80,
        confidence_breakdown={"reference_present": 12},
        invoice_date=date(2026, 7, 10),
        total_gross=Decimal("123.00"),
        seller=DocumentPartyDto(
            tax_number="6431668510", name="DOMBUD", street=None, zip_code=None, city=None,
            company=seller_company,
        ),
        buyer=DocumentPartyDto(
            tax_number=None, name="Jan Kowalski", street="Leśna 1", zip_code="00-001", city="Warszawa",
            company=None,
            suggestions=[CompanySummaryDto(id=uuid4(), name="Kowalski Jan", tax_number="OTH-000001", to_verify=False)],
        ),
        candidates=[MatchCandidateDto(
            record_id=uuid4(), reference="PRO/1", status="new_cost", invoice_date=date(2026, 7, 1),
            total_gross=Decimal("125.00"), seller_name="DOMBUD", buyer_name="Remontivo",
            reasons=("names", "total"), same_seller=True, same_buyer=False,
            total_difference=Decimal("2.00"),
        )],
    )


def _client(execute) -> TestClient:
    app = FastAPI()
    app.state.templates = Jinja2Templates(directory=str(API_DIR / "templates"))

    @app.middleware("http")
    async def fake_ctx(request, call_next):
        request.state.ctx = SimpleNamespace(user_id=uuid4(), organization_id=uuid4())
        return await call_next(request)

    services = SimpleNamespace(
        action_bus=SimpleNamespace(execute=execute),
        get_document_service=object(),
        apply_document_service=object(),
        log_business_event_service=object(),
    )
    app.dependency_overrides[get_services] = lambda: services
    app.include_router(documents.router)
    return TestClient(app)


def test_match_screen_renders_parties_candidates_and_actions():
    response = _client(lambda **_: _dto()).get(f"/documents/{DOC_ID}/match")

    assert response.status_code == 200
    html = response.text
    assert 'id="company-slot-seller"' in html and "DOMBUD" in html
    assert "Nie ma firmy o tym NIP-ie" in html          # nabywca nieznany
    assert "Kowalski Jan (OTH-000001)" in html          # podpowiedź
    assert "Utwórz firmę z danych dokumentu" in html
    assert "PRO/1" in html and "różnica 2.00" in html
    assert ">nazwy<" in html and ">suma<" in html
    assert 'value="ADD_TO_EXISTING"' in html
    assert f'hx-post="/documents/{DOC_ID}/delete"' in html


def _apply(client, **form):
    data = {"action": "CREATE_NEW", "from_screen": "1", **form}
    return client.post(f"/documents/{DOC_ID}/apply", data=data)


def test_create_from_screen_requires_both_parties():
    calls = []
    response = _apply(_client(lambda **kw: calls.append(kw)), seller_tax_number="6431668510")

    assert "Wybierz sprzedawcę i nabywcę" in response.text
    assert calls == []


def test_create_from_screen_passes_chosen_parties_and_redirects():
    calls = []

    def execute(**kwargs):
        calls.append(kwargs)
        return uuid4()

    response = _apply(_client(execute), seller_tax_number="6431668510", buyer_tax_number="OTH-000001")

    command = calls[0]["action"]
    assert command.override_seller_nip == "6431668510"
    assert command.override_buyer_nip == "OTH-000001"
    assert json.loads(response.headers["HX-Location"])["path"] == "/documents"


def test_seller_mismatch_asks_for_confirmation():
    def execute(**_):
        raise SellerMismatchError(document_seller_nip="1", record_seller_id=uuid4())

    response = _apply(
        _client(execute),
        action="ADD_TO_EXISTING", target_record_id=str(uuid4()), document_source="ksef",
    )

    assert "Przypnij mimo to" in response.text
    assert "Przepnij rekord na sprzedawcę z KSeF" in response.text


def test_delete_from_screen_returns_to_documents_list():
    calls = []
    client = _client(lambda **kw: calls.append(kw))
    client.app.dependency_overrides[get_services]().delete_document_service = object()

    response = client.post(f"/documents/{DOC_ID}/delete", data={"from_screen": "1"})

    assert calls[0]["action"].document_id == DOC_ID
    assert json.loads(response.headers["HX-Location"])["path"] == "/documents"
