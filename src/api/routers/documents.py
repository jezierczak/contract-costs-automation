import json
import logging
from html import escape as html_escape
from datetime import date, timedelta
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from starlette.responses import HTMLResponse, Response
import shutil

from api.dependencies import get_services
from contract_costs.model.business_event import BusinessEventLevel
from contract_costs.model.company import CompanyType
from contract_costs.ksef.render.invoice_visualisation import PRINT_CSS, ksef_verification_url, render_invoice_html
from contract_costs.model.document import DocumentType, DocumentStatus
from contract_costs.services.business_event.business_event_helper import BusinessEventHelper
from contract_costs.services.companies.query.dto.company_query import CompanyQuery
from contract_costs.services.documents.apply.dto.apply_document_command import ApplyDocumentCommand, DocumentApplyAction
from contract_costs.services.documents.exeptions import DuplicateDocument
from contract_costs.services.documents.process.delete.delete_document_command import DeleteDocumentCommand
from contract_costs.services.documents.process.unattach.unattach_document_command import UnattachDocumentCommand
from contract_costs.services.documents.query.dto.get_document_file_query import GetDocumentFileQuery
from contract_costs.services.documents.query.dto.get_document_query import GetDocumentQuery
from contract_costs.services.documents.query.list_docuemnts_query_command import (
    ListDocumentsQueryCommand,
)
from contract_costs.services.documents.upload.dto.upload_document_command import UploadDocumentCommand
from contract_costs.services.ksef.dto.enqueue_ksef_auto_import_command import EnqueueKsefAutoImportCommand
from contract_costs.services.queue.ksef_import_queue import ksef_import_queue
from contract_costs.services.workers.dto.ksef_import_queue_item import KsefImportQueueItem
import contract_costs.config as cfg
router = APIRouter()

logger = logging.getLogger(__name__)

# pasek nad zapasową wizualizacją XSL MF (?mf=1); „Drukuj” z arkuszem wydruku A4
_PRINT_TOOLBAR = """
<style>@media print { .cc-print-toolbar { display: none !important; } __PRINT_CSS__ }</style>
<div class="cc-print-toolbar" style="position:sticky;top:0;z-index:10;display:flex;gap:8px;justify-content:flex-end;
     padding:8px 5%;background:#f3f4f6;border-bottom:1px solid #d1d5db;font-family:Arial,sans-serif;font-size:13px">
    <button type="button" onclick="window.print()"
            style="padding:4px 12px;border:1px solid #9ca3af;border-radius:4px;background:#fff;cursor:pointer">
        Drukuj
    </button>
    <a href="?raw=1" style="padding:4px 12px;color:#374151">Surowy XML</a>
</div>
""".replace("__PRINT_CSS__", PRINT_CSS)


def _with_print_toolbar(html: str) -> str:
    body_start = html.find("<body")
    if body_start < 0:
        return _PRINT_TOOLBAR + html
    body_end = html.find(">", body_start) + 1
    return html[:body_end] + _PRINT_TOOLBAR + html[body_end:]


def _qr_code_for(path: Path) -> str:
    try:
        return ksef_verification_url(path) or ""
    except Exception:
        logger.exception("Cannot build KSeF QR link for %s", path)
        return ""


def _render_documents_table(
    *,
    request: Request,
    services,
    ctx,
    status: str | None = None,
):
    if not status:
        status = None
    documents = services.action_bus.execute(
        action=ListDocumentsQueryCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            status=DocumentStatus(status) if status else None,

        ),
        handler=services.list_documents_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "documents/_table.html",
        {
            "request": request,
            "documents": documents,
            "current_status": status,
        },
    )


def _render_ksef_import_modal(
    *,
    request: Request,
    own_companies: list,
    error_message: str | None = None,
):
    today = date.today()
    return request.app.state.templates.TemplateResponse(
        "documents/_ksef_import_modal.html",
        {
            "request": request,
            "own_companies": own_companies,
            "default_from_date": (today - timedelta(days=7)).isoformat(),
            "default_to_date": today.isoformat(),
            "error_message": error_message,
        },
    )

@router.get("/documents", response_class=HTMLResponse)
def documents_list(
    request: Request,
    has_payload: bool | None = None,
    has_record: bool | None = None,
    source: str | None = None,
    status: str | None = None,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    documents = services.action_bus.execute(
        action=ListDocumentsQueryCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            has_payload=has_payload,
            has_record=has_record,
            source=source,
            status=DocumentStatus(status) if status else None,
        ),
        handler=services.list_documents_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "documents/page.html",
        {
            "request": request,
            "title": "Dokumenty",
            "documents": documents,
            "has_payload": has_payload,
            "has_record": has_record,
            "source": source,
            "current_status": status
        },
    )

from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse


@router.get("/documents/{document_id}/file")
def document_file(
    request: Request,
    document_id: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    dto = services.action_bus.execute(
        action=GetDocumentFileQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            document_id=UUID(document_id),
        ),
        handler=services.get_document_file_service,
    )

    path = Path(dto.file_path)

    if not path.is_file():
        logger.error("Document %s file missing on disk: %s", document_id, path)
        return HTMLResponse(
            f"<p>Brak pliku dokumentu na dysku: <code>{html_escape(str(path))}</code></p>",
            status_code=404,
        )

    download = request.query_params.get("download")
    raw = request.query_params.get("raw")

    # ==========================================
    # DOWNLOAD
    # ==========================================

    if download:
        # XML jako oryginał – PDF daje podgląd (generator MF w przeglądarce)
        # Starlette sam koduje nazwę (filename*=utf-8''…) – ręczny nagłówek
        # wywracał się na polskich znakach
        return FileResponse(path, filename=path.name)

    # ==========================================
    # XML PREVIEW
    # ==========================================

    if path.suffix.lower() == ".xml" and not raw and not request.query_params.get("mf"):
        # PDF generuje w przeglądarce oficjalna biblioteka MF (jak w aplikacji KSeF)
        return request.app.state.templates.TemplateResponse(
            request,
            "documents/invoice_preview.html",
            {
                "file_name": path.name,
                "pdf_name": path.stem + ".pdf",
                "ksef_number": dto.ksef_number or "",
                "qr_code": _qr_code_for(path) if dto.ksef_number else "",
            },
        )

    if path.suffix.lower() == ".xml" and not raw:
        try:
            return HTMLResponse(_with_print_toolbar(render_invoice_html(path)))
        except Exception:
            logger.exception("XML visualisation failed for document %s", document_id)
            return FileResponse(path)

    # ==========================================
    # RAW XML lub inne pliki
    # ==========================================

    return FileResponse(path)

@router.get("/documents/{document_id}/match-data")
def document_match_data(
    request: Request,
    document_id: str,
    services=Depends(get_services),
):
    """Surowe dane ekranu dopasowania (JSON) – do sprawdzenia przed widokiem."""
    ctx = request.state.ctx
    document = services.action_bus.execute(
        action=GetDocumentQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            document_id=UUID(document_id),
        ),
        handler=services.get_document_service,
    )
    return JSONResponse(jsonable_encoder(document))


@router.get("/documents/{document_id}/apply-form")
def document_apply_form(
    request: Request,
    document_id: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    document = services.action_bus.execute(
        action=GetDocumentQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            document_id=UUID(document_id),
        ),
        handler=services.get_document_service,
    )

    return request.app.state.templates.TemplateResponse(
        "documents/_apply_modal.html",
        {
            "request": request,
            "document": document,
            "doc_types": [v.value for v in DocumentType]
        },
    )

@router.get("/documents/upload-form")
def document_upload_form(
    request: Request,
):
    return request.app.state.templates.TemplateResponse(
        "documents/_upload_modal.html",
        {
            "request": request,
        },
    )


@router.get("/documents/ksef/import-form")
def documents_ksef_import_form(
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx
    own_companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            include_inactive=False,
            role=CompanyType.OWN,
        ),
        handler=services.company_query_service,
    )
    return _render_ksef_import_modal(
        request=request,
        own_companies=own_companies,
    )


@router.post("/documents/ksef/import")
def documents_ksef_import(
    request: Request,
    company_id: UUID = Form(...),
    from_date: str = Form(...),
    to_date: str = Form(...),
    services=Depends(get_services),
):
    ctx = request.state.ctx
    own_companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            include_inactive=False,
            role=CompanyType.OWN,
        ),
        handler=services.company_query_service,
    )
    own_company = next((c for c in own_companies if c.id == company_id), None)
    if own_company is None:
        return _render_ksef_import_modal(
            request=request,
            own_companies=own_companies,
            error_message="Wybrana firma own nie istnieje albo jest nieaktywna.",
        )

    try:
        from_dt = date.fromisoformat(from_date)
        to_dt = date.fromisoformat(to_date)
    except ValueError:
        return _render_ksef_import_modal(
            request=request,
            own_companies=own_companies,
            error_message="Niepoprawny format daty.",
        )

    if from_dt > to_dt:
        return _render_ksef_import_modal(
            request=request,
            own_companies=own_companies,
            error_message="Data od nie moze byc wieksza niz data do.",
        )

    with services.uow as uow:
        settings = uow.company_ksef_settings.get_by_company_id(
            organization_id=ctx.organization_id,
            company_id=company_id,
        )

    if not settings or not settings.is_enabled:
        return _render_ksef_import_modal(
            request=request,
            own_companies=own_companies,
            error_message="Brak aktywnej konfiguracji KSeF dla wybranej firmy.",
        )

    # Krok 1: tylko zlecenie importu (UI + endpoint).
    # Docelowe pobieranie z API KSeF bedzie realizowane przez KsefImportWorker.
    ksef_import_queue.put(
        KsefImportQueueItem(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            company_id=own_company.id,
            from_date=from_dt,
            to_date=to_dt,
        )
    )

    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message=(
            f"Zlecono import KSeF dla {own_company.name} "
            f"({from_dt.isoformat()} - {to_dt.isoformat()})"
        ),
        entity_type="company",
        entity_id=own_company.id,
    )

    response = Response(status_code=200)
    response.headers["HX-Trigger"] = (
        '{"closeModal": true, '
        '"showMessage": {"type": "success", "text": "Zlecenie importu KSeF zapisane."}}'
    )
    return response

@router.post("/documents/ksef/import-auto")
def documents_ksef_import_auto(
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx
    result = services.action_bus.execute(
        action=EnqueueKsefAutoImportCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
        ),
        handler=services.enqueue_ksef_auto_import_service,
    )

    for company in result.enqueued:
        BusinessEventHelper.log(
            services=services,
            ctx=ctx,
            level=BusinessEventLevel.INFO,
            message=f"Zlecono automatyczny import KSeF dla {company.name} (od ostatniego pobrania)",
            entity_type="company",
            entity_id=company.id,
        )

    parts = []
    if result.enqueued:
        parts.append(
            "Zlecono import KSeF: " + ", ".join(c.name for c in result.enqueued) + "."
        )
    if result.missing_first_import:
        parts.append(
            "Pominięto (wykonaj najpierw jednorazowy import ręczny): "
            + ", ".join(c.name for c in result.missing_first_import)
            + "."
        )
    if not parts:
        parts.append("Brak firm własnych z aktywną konfiguracją KSeF.")

    response = Response(status_code=200)
    response.headers["HX-Trigger"] = json.dumps({
        "showMessage": {
            "type": "success" if result.enqueued else "error",
            "text": " ".join(parts),
        },
    })
    return response

@router.get("/documents/table")
def documents_table(request: Request,
                    status: str | None = None,
                    services=Depends(get_services)):
    ctx = request.state.ctx
    return _render_documents_table(
        request=request,
        services=services,
        ctx=ctx,
        status=status
    )




@router.post("/documents/upload")
async def upload_documents(
    request: Request,
    files: list[UploadFile] = File(...),
    services=Depends(get_services),
):
    ctx = request.state.ctx

    incoming_dir = (
        cfg.WORK_DIR
        / str(ctx.organization_id)
        / cfg.DOCUMENTS_DIR
        / "incoming"
    )
    incoming_dir.mkdir(parents=True, exist_ok=True)

    for file in files:

        file_path = incoming_dir / file.filename

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 🚀 start pipeline

        try:
            entity_id= services.action_bus.execute(
                action=UploadDocumentCommand(
                    organization_id=ctx.organization_id,
                    actor_user_id=ctx.user_id,
                    file_path=file_path,
                ),
                handler=services.upload_document_service,
            )
            BusinessEventHelper.log(
                services=services,
                ctx=ctx,
                level=BusinessEventLevel.SUCCESS,
                message=f"Dodano dokument: {file.filename}",
                entity_type="document",
                entity_id=entity_id
            )
        except DuplicateDocument as e:

            BusinessEventHelper.log(
                services=services,
                ctx=ctx,
                level=BusinessEventLevel.ERROR,
                message=f"Wykryto duplikat dokumentu",
                entity_type="document",
                entity_id=e.document_id,
            )

    response = _render_documents_table(
        request=request,
        services=services,
        ctx=ctx,
    )
    response.headers["HX-Trigger"] = "documentsUploaded"

    return response

@router.post("/documents/{document_id}/apply")
def apply_document(
    request: Request,
    document_id: str,

    action: str = Form(...),
    target_record_id: str | None = Form(None),

    override_document_type: str | None = Form(None),
    override_document_number: str | None = Form(None),
    override_seller_nip: str | None = Form(None),

    confirm_seller_mismatch: int = Form(0),
    relink_record_seller: int = Form(0),

    services=Depends(get_services),
):
    ctx = request.state.ctx
    apply_action = DocumentApplyAction(action)

    command = ApplyDocumentCommand(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,
        document_id=UUID(document_id),
        action=apply_action,
        target_record_id=UUID(target_record_id) if target_record_id else None,
        override_document_type=override_document_type,
        override_document_number=override_document_number,
        override_seller_nip=override_seller_nip,
        confirm_seller_mismatch=bool(confirm_seller_mismatch),
        relink_record_seller=bool(relink_record_seller),
    )

    assigned_record_id = services.action_bus.execute(
        action=command,
        handler=services.apply_document_service,
    )

    match apply_action:
        case DocumentApplyAction.CREATE_NEW:
            message = "Utworzono nowy rekord na bazie dokumentu"
        case DocumentApplyAction.ADD_TO_EXISTING:
            message = "Przypisano dokument do istniejącego rekordu"
        case _:
            message = "Nieznana opcja"

    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.SUCCESS,
        message=message,
        entity_type="record",
        entity_id=assigned_record_id if assigned_record_id else None,
    )
    response = _render_documents_table(
        request=request,
        services=services,
        ctx=ctx,
    )

    response.headers["HX-Trigger"] = "documentsUploaded"

    return response

@router.post("/documents/{document_id}/unattach")
def unattach_document(
        request: Request,
        document_id: str,
        services = Depends(get_services)
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=UnattachDocumentCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            document_id=UUID(document_id),
        ),
        handler=services.unattach_document_service,
    )
    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message="Odłączono dokument od wpisu",
        entity_type="document",
        entity_id=UUID(document_id),
    )


    return _render_documents_table(
        request=request,
        services=services,
        ctx=ctx,
    )

@router.post("/documents/{document_id}/delete")
def delete_document(
    request: Request,
    document_id: str,

    services=Depends(get_services),
):
    ctx = request.state.ctx
    services.action_bus.execute(
        action=DeleteDocumentCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            document_id=UUID(document_id),
        ),
        handler=services.delete_document_service,
    )
    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message="Usunięto dokument",
        entity_type="document",
        entity_id=UUID(document_id),
    )

    return _render_documents_table(
        request=request,
        services=services,
        ctx=ctx,
    )
