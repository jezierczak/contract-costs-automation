from io import BytesIO
from uuid import UUID
from lxml import etree
from pathlib import Path
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from starlette.responses import HTMLResponse, Response
import shutil

from xhtml2pdf import pisa

from api.dependencies import get_services
from contract_costs.model.business_event import BusinessEventLevel
from contract_costs.model.document import DocumentType, DocumentStatus
from contract_costs.services.business_event.business_event_helper import BusinessEventHelper
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
import contract_costs.config as cfg
router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]

xslt_path = BASE_DIR / "src" / "contract_costs" / "resources" / "fa3_visualisation_v2.xslt"

def render_xml_preview(xml_path):
    xml = etree.parse(str(xml_path))
    xslt = etree.parse(str(xslt_path))
    transform = etree.XSLT(xslt)
    result = transform(xml)
    return str(result)

def render_xml_to_pdf(xml_path: Path) -> bytes:

    # XML
    xml = etree.parse(str(xml_path))

    # XSLT
    xslt = etree.parse(str(xslt_path))
    transform = etree.XSLT(xslt)

    # HTML z transformacji
    html_tree = transform(xml)
    html_string = etree.tostring(html_tree, encoding="unicode")

    # PDF
    pdf_buffer = BytesIO()

    pisa.CreatePDF(
        html_string.encode("utf-8"),  # 👈 ważne
        dest=pdf_buffer,
    )

    return pdf_buffer.getvalue()

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

from fastapi.responses import FileResponse


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

    download = request.query_params.get("download")
    raw = request.query_params.get("raw")

    # ==========================================
    # DOWNLOAD
    # ==========================================

    if download:

        # XML → generuj PDF
        if path.suffix.lower() == ".xml":
            pdf = render_xml_to_pdf(path)

            filename = path.stem + ".pdf"

            return Response(
                content=pdf,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                },
            )

        # inne pliki
        return FileResponse(
            path,
            filename=path.name,
            headers={
                "Content-Disposition": f'attachment; filename="{path.name}"'
            },
        )

    # ==========================================
    # XML PREVIEW
    # ==========================================

    if path.suffix.lower() == ".xml" and not raw:
        try:
            html = render_xml_preview(path)
            return HTMLResponse(html)
        except Exception:
            return FileResponse(path)

    # ==========================================
    # RAW XML lub inne pliki
    # ==========================================

    return FileResponse(path)

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