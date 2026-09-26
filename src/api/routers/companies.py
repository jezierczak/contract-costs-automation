import json
import shutil
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from starlette.responses import HTMLResponse

import contract_costs.config as cfg
from api.dependencies import get_services
from contract_costs.model.company import CompanyType, Address, Contact, BankAccount, ReferenceNumberingMode
from contract_costs.model.company_ksef_settings import KsefEnvironment
from contract_costs.services.companies.dto.create_company_command import CreateOwnerCompanyCommand, \
    CreateCounterpartyCompanyCommand
from contract_costs.services.companies.dto.deactivate_company_command import DeactivateOwnerCompanyCommand, \
    DeactivateCounterpartyCompanyCommand
from contract_costs.services.companies.dto.update_company_command import UpdateOwnerCompanyCommand, \
    UpdateCounterpartyCompanyCommand
from contract_costs.services.companies.query.dto.company_detail_query import CompanyDetailQuery
from contract_costs.services.companies.query.dto.company_query import CompanyQuery
from contract_costs.services.companies.dto.save_company_ksef_settings_command import SaveCompanyKsefSettingsCommand

COMPANY_NUMBERING_OPTIONS = [
    {"value": "", "label": "Nie generuj — numer wpisywany ręcznie"},
    {"value": ReferenceNumberingMode.MONTHLY.value, "label": "Automatyczna miesięczna"},
    {"value": ReferenceNumberingMode.YEARLY.value, "label": "Automatyczna roczna"},
    {"value": ReferenceNumberingMode.GLOBAL.value, "label": "Automatyczna globalna"},
]

router = APIRouter()


def _render_ksef_settings_modal(
    *,
    request: Request,
    company,
    settings=None,
    success_message: str | None = None,
    error_message: str | None = None,
):
    return request.app.state.templates.TemplateResponse(
        "companies/_ksef_settings_modal.html",
        {
            "request": request,
            "company": company,
            "settings": settings,
            "environments": [env.value for env in KsefEnvironment],
            "success_message": success_message,
            "error_message": error_message,
        },
    )


def gus_lookup(nip: str):

    # tu możesz użyć:
    # GUS API
    # VIES
    # REGON API

    return {
        "name": "Budremex Sp. z o.o.",
        "street": "ul. Krakowska 10",
        "city": "Kraków",
        "zip_code": "30-001",
    }

@router.post("/companies/create-own")
def create_owner_company(
    request: Request,

    name: str = Form(...),
    tax_number: str = Form(...),
    description: str | None = Form(None),

    street: str | None = Form(None),
    city: str | None = Form(None),
    zip_code: str | None = Form(None),
    country: str | None = Form(None),

    phone_number: str | None = Form(None),
    email: str | None = Form(None),

    account_number: str | None = Form(None),
    country_code: str | None = Form(None),


    next_page: str | None = Form(None),

    services=Depends(get_services),
):

    ctx = request.state.ctx
    address = Address(
        street=street,
        city=city,
        zip_code=zip_code,
        country=country,
    )

    contact = Contact(
        phone_number=phone_number,
        email=email,
    )

    bank_account = BankAccount(
        account_number=account_number,
        country_code=country_code,
    )
    command = CreateOwnerCompanyCommand(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,
        name=name,
        tax_number=tax_number,
        role=CompanyType.OWN,
        description=description,
        address=address,
        contact=contact,
        bank_account=bank_account,
        tags=set(),
    )

    services.action_bus.execute(
        action=command,
        handler=services.create_company,
    )

    if next_page:
        return RedirectResponse(next_page, status_code=303)

    return RedirectResponse(
        url=f"/companies/{tax_number}",
        status_code=303,
    )
@router.get("/companies/gus", response_class=HTMLResponse)
def company_gus_lookup(
    request: Request,
    tax_number: str | None = None,
):
    if not tax_number:
        return HTMLResponse("")

    company = gus_lookup(tax_number)

    if not company:
        return HTMLResponse(
            "<div class='text-sm text-red-600 mt-2'>Nie znaleziono firmy w GUS</div>"
        )

    return request.app.state.templates.TemplateResponse(
        "companies/_gus_autofill.html",
        {
            "request": request,
            "company": company,
        },
    )

@router.get("/companies/new", response_class=HTMLResponse)
def company_new(
    request: Request,
    target: str | None = None,
):
    return request.app.state.templates.TemplateResponse(
        "companies/new.html",
        {
            "request": request,
            "company": None,
            "title": "Nowa firma - kontrahent",
            "action_url": "/companies/create",
            "submit_label": "Dodaj",
            "show_role": True,
            "company_roles": [r.value for r in CompanyType if r.name != "OWN"],
            "picker_target": target,
            "return_to_picker": bool(target),
        },
    )

@router.get("/companies/new-owner", response_class=HTMLResponse)
def company_new_owner(
    request: Request,
):
    return request.app.state.templates.TemplateResponse(
        "companies/new_owner.html",
        {
            "request": request,
            "company": None,
            "title": "Nowa firma własna",
            "action_url": "/companies/create-own",
            "submit_label": "Dodaj",
            "show_role": False,  # ukryta rola
        },
    )
@router.get("/companies", response_class=HTMLResponse)
def companies_page(
    request: Request,
):
    return request.app.state.templates.TemplateResponse(
        "companies/page.html",
        {
            "request": request,
            "company_types": CompanyType,
        },
    )

@router.get("/companies/table", response_class=HTMLResponse)
def companies_table(
    request: Request,
    search: str | None = None,
    role: str | None = None,
    inactive: int = 0,
    sort_by: str | None = None,
    sort_dir: str | None = None,
    mode: str = "manage",
    target: str | None = None,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    role_enum = CompanyType(role) if role else None

    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            search=search,
            role=role_enum,
            include_inactive=bool(inactive),
            sort_by=sort_by,
            sort_dir=sort_dir,
        ),
        handler=services.company_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "companies/_table.html",
        {
            "request": request,
            "companies": companies,
            "mode": mode,
            "target": target,
        },
    )

@router.get("/companies/picker")
def companies_picker(
    request: Request,
    target: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
        ),
        handler=services.company_query_service,
    )
    company_types = list(CompanyType)

    return request.app.state.templates.TemplateResponse(
        "companies/_picker_modal.html",
        {
            "request": request,
            "companies": companies,
            "target": target,
            "company_types": company_types,
            "selected_company_type": None,
        },
    )

@router.get("/companies/select")
def company_select(
    request: Request,
    tax_number: str,
    target: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            tax_number=tax_number,
        ),
        handler=services.company_query_service,
    )
    company = companies[0] if companies else None
    # print(target)
    # print(company)

    return request.app.state.templates.TemplateResponse(
        "companies/_selected_company_slot.html",
        {
            "request": request,
            "company": company,
            "target": target,
        },
    )

@router.get("/companies/picker/table")
def companies_picker_table(
    request: Request,
    target: str,
    search: str | None = None,
    company_type: str | None = None,
    include_inactive: str | None = None,
    services=Depends(get_services),
):
    ctx = request.state.ctx
    include_inactive_bool = include_inactive == "1"
    role = CompanyType(company_type) if company_type else None
    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            search=search,
            include_inactive=include_inactive_bool,
            role=role

        ),
        handler=services.company_query_service,
    )
    company_types = list(CompanyType)

    return request.app.state.templates.TemplateResponse(
        "companies/_picker_table.html",
        {
            "request": request,
            "companies": companies,
            "target": target,
            "company_types": company_types,
            "selected_company_type": company_type,
        },
    )

from fastapi import HTTPException


def _get_company(
    *,
    ctx,
    services,
    tax_number: str | None = None,
    company_id: UUID | None = None,
):

    if company_id is not None:
        action = CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            company_id=company_id,
        )

    elif tax_number is not None:
        action = CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            tax_number=tax_number,
        )

    else:
        raise HTTPException(status_code=404, detail="Company identifier missing")

    companies = services.action_bus.execute(
        action=action,
        handler=services.company_query_service,
    )

    if not companies:
        raise HTTPException(status_code=404, detail="Company not found")

    return companies[0]

@router.get("/companies/{tax_number}", response_class=HTMLResponse)
def company_detail(
    request: Request,
    tax_number: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    company = _get_company(ctx=ctx, tax_number=tax_number, services=services)

    return request.app.state.templates.TemplateResponse(
        "companies/details/page.html",
        {
            "request": request,
            "company": company,

        },
    )

@router.get("/companies/{tax_number}/content", response_class=HTMLResponse)
def company_detail_content(
    request: Request,
    tax_number: str,
    owner_company_id: str | None = None,
    services = Depends(get_services),
):
    ctx = request.state.ctx


    company = _get_company(ctx=ctx, tax_number=tax_number, services=services)

    dashboard = services.action_bus.execute(
        action=CompanyDetailQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            company_id=company.id,
            owner_company_id=UUID(owner_company_id) if owner_company_id else None,
        ),
        handler=services.company_detail_query_service,
    )

    owner_companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            own_only=True
        ),
        handler=services.company_query_service,
    )


    return request.app.state.templates.TemplateResponse(
        "companies/details/_content.html",
        {
            "request": request,
            "company": company,
            "dashboard": dashboard,
            "owner_companies": owner_companies,
            "selected_owner_company_id": owner_company_id,
        },
    )

@router.get("/companies/{company_id}/metadata")
def company_metadata(
    request: Request,
    company_id: UUID,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    company = _get_company(ctx=ctx, company_id=company_id, services=services)

    return request.app.state.templates.TemplateResponse(
        "companies/details/_metadata.html",
        {
            "request": request,
            "company": company,
        },
    )

@router.get("/companies/{tax_number}/edit", response_class=HTMLResponse)
def company_edit_panel(
    request: Request,
    tax_number: str,
    target: str | None = None,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            tax_number=tax_number
        ),
        handler=services.company_query_service,
    )

    if not companies:
        return HTMLResponse(status_code=404)

    company=companies[0]

    return request.app.state.templates.TemplateResponse(
        "companies/edit.html",
        {
            "request": request,
            "company": company,
            "title": "Edytuj firmę",
            "subtitle": "",
            "action_url": f"/companies/update",
            "submit_label": "Zapisz",
            "show_role": True if company.role != CompanyType.OWN else False,
            "company_roles": [r.value for r in CompanyType if r.name != "OWN"],
            "numbering_options": COMPANY_NUMBERING_OPTIONS,
            "picker_target": target,
            "return_to_picker": False,
        },
    )

@router.get("/companies/{company_id}/metadata-modal")
def company_metadata_modal(
    request: Request,
    company_id: UUID,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    company = _get_company(ctx=ctx, company_id=company_id, services=services)

    return request.app.state.templates.TemplateResponse(
        "own_company_dashboard/_company_metadata_modal.html",
        {
            "request": request,
            "company": company,
        },
    )


@router.get("/companies/{company_id}/ksef-settings")
def company_ksef_settings_modal(
    request: Request,
    company_id: UUID,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    company = _get_company(ctx=ctx, company_id=company_id, services=services)

    if company.role.value != "Own":
        raise HTTPException(status_code=404)

    with services.uow as uow:
        settings = uow.company_ksef_settings.get_by_company_id(
            organization_id=ctx.organization_id,
            company_id=company_id,
        )

    return _render_ksef_settings_modal(
        request=request,
        company=company,
        settings=settings,
    )


@router.post("/companies/{company_id}/ksef-settings")
def company_ksef_settings_save(
    request: Request,
    company_id: UUID,
    environment: str = Form(...),
    is_enabled: str | None = Form(None),
    certificate_file: UploadFile | None = File(None),
    certificate_password: str | None = Form(None),
    last_import_from: str | None = Form(None),
    services=Depends(get_services),
):
    ctx = request.state.ctx

    company = _get_company(ctx=ctx, company_id=company_id, services=services)

    if company.role.value != "Own":
        raise HTTPException(status_code=404)

    try:
        certificate_path = None
        if certificate_file is not None and certificate_file.filename:
            suffix = certificate_file.filename.rsplit(".", 1)[-1].lower() if "." in certificate_file.filename else ""
            if suffix not in {"p12", "pfx"}:
                raise ValueError("Certyfikat musi byc plikiem .p12 lub .pfx")

            certs_dir = cfg.WORK_DIR / str(ctx.organization_id) / cfg.KSEF_CERTS_DIR
            certs_dir.mkdir(parents=True, exist_ok=True)
            certificate_path = certs_dir / f"{company_id}.{suffix}"
            with open(certificate_path, "wb") as f:
                shutil.copyfileobj(certificate_file.file, f)
            # zapis w formacie POSIX, żeby ścieżka działała i na Windows, i w kontenerze Linux
            certificate_path = certificate_path.as_posix()

        settings = services.action_bus.execute(
            action=SaveCompanyKsefSettingsCommand(
                organization_id=ctx.organization_id,
                actor_user_id=ctx.user_id,
                company_id=company_id,
                environment=KsefEnvironment(environment),
                is_enabled=is_enabled == "1",
                certificate_path=certificate_path,
                certificate_password=(certificate_password or "").strip() or None,
                last_import_from=date.fromisoformat(last_import_from) if last_import_from else None,
            ),
            handler=services.save_company_ksef_settings_service,
        )
    except Exception as exc:
        with services.uow as uow:
            current_settings = uow.company_ksef_settings.get_by_company_id(
                organization_id=ctx.organization_id,
                company_id=company_id,
            )
        return _render_ksef_settings_modal(
            request=request,
            company=company,
            settings=current_settings,
            error_message=str(exc),
        )

    return _render_ksef_settings_modal(
        request=request,
        company=company,
        settings=settings,
        success_message="Ustawienia KSeF zapisane.",
    )




@router.post("/companies/create")
def company_create(
        request: Request,

        name: str = Form(...),
        tax_number: str = Form(...),
        description: str | None = Form(None),

        street: str | None = Form(None),
        city: str | None = Form(None),
        zip_code: str | None = Form(None),
        country: str | None = Form(None),

        phone_number: str | None = Form(None),
        email: str | None = Form(None),

        account_number: str | None = Form(None),
        country_code: str | None = Form(None),

        role: str = Form(...),
        picker_target: str | None = Form(None),

        services=Depends(get_services),
):
    ctx = request.state.ctx
    address = Address(
        street=street,
        city=city,
        zip_code=zip_code,
        country=country,
    )

    contact = Contact(
        phone_number=phone_number,
        email=email,
    )

    bank_account = BankAccount(
        account_number=account_number,
        country_code=country_code,
    )

    role_enum = CompanyType(role)
    command = CreateCounterpartyCompanyCommand(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,
        name=name,
        tax_number=tax_number,
        role=role_enum,
        description=description,
        address=address,
        contact=contact,
        bank_account=bank_account,
        tags=set(),
    )

    company = services.action_bus.execute(
        action=command,
        handler=services.create_company,
    )

    if picker_target:
        response = request.app.state.templates.TemplateResponse(
            "companies/_selected_company_slot.html",
            {
                "request": request,
                "company": company,
                "target": picker_target,
            },
        )
    else:
        response = HTMLResponse("")

    response.headers["HX-Trigger"] = json.dumps({
        "showMessage": {
            "type": "success",
            "text": f"Zaktualizowano firmę {name}"
        },
        "companiesChanged": True
    })

    response.headers["HX-Trigger-After-Swap"] = json.dumps({
        "closeModal": True
    })

    return response


@router.post("/companies/update")
def company_update(
    request: Request,

    company_id: str = Form(...),

    name: str = Form(...),
    tax_number: str = Form(...),
    role: str | None = Form(None),
    description: str | None = Form(None),

    street: str | None = Form(None),
    city: str | None = Form(None),
    zip_code: str | None = Form(None),
    country: str | None = Form(None),

    phone_number: str | None = Form(None),
    email: str | None = Form(None),

    account_number: str | None = Form(None),
    country_code: str | None = Form(None),
    picker_target: str | None = Form(None),
    # brak pola = nie zmieniaj; "" = numer wpisywany ręcznie
    reference_numbering_mode: str | None = Form(None),

    services=Depends(get_services),
):
    ctx = request.state.ctx

    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
        ),
        handler=services.company_query_service,
    )

    company = next((c for c in companies if str(c.id) == company_id), None)

    final_role = CompanyType(role) if role else company.role

    base_kwargs = dict(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,
        company_id=company_id,
        name=name,
        tax_number=tax_number,
        description=description,
        address=Address(
            street=street,
            city=city,
            zip_code=zip_code,
            country=country,
        ),
        contact=Contact(
            phone_number=phone_number,
            email=email,
        ),
        bank_account=BankAccount(
            account_number=account_number,
            country_code=country_code,
        ),
        role=final_role,
        tags=set(),
        set_reference_numbering_mode=reference_numbering_mode is not None,
        reference_numbering_mode=(
            ReferenceNumberingMode(reference_numbering_mode) if reference_numbering_mode else None
        ),
    )
    if final_role == CompanyType.OWN:
        command = UpdateOwnerCompanyCommand(**base_kwargs)
    else:
        command = UpdateCounterpartyCompanyCommand(**base_kwargs)

    services.action_bus.execute(
        action=command,
        handler=services.update_company_service,
    )

    if picker_target:
        response = request.app.state.templates.TemplateResponse(
            "companies/_selected_company_slot.html",
            {
                "request": request,
                "company": {
                    "name": name,
                    "tax_number": tax_number,
                },
                "target": picker_target,
            },
        )
    else:
        response = HTMLResponse("")

    response.headers["HX-Trigger"] = json.dumps({
        "showMessage": {
            "type": "success",
            "text": f"Zaktualizowano firmę {name}"
        },
        "companiesChanged": True,
        "companyUpdated": True
    })

    response.headers["HX-Trigger-After-Swap"] = json.dumps({
        "closeModal": True
    })

    return response

@router.post("/companies/{company_id}/deactivate")
def company_deactivate(
    request: Request,
    company_id: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
        ),
        handler=services.company_query_service,
    )

    company = next((c for c in companies if str(c.id) == company_id), None)

    if company.role == CompanyType.OWN:
        command = DeactivateOwnerCompanyCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            company_id=company.id,
        )
    else:
        command = DeactivateCounterpartyCompanyCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            company_id=company.id,
        )

    services.action_bus.execute(
        action=command,
        handler=services.deactivate_company_service,
    )


    response = HTMLResponse("")

    response.headers["HX-Trigger"] = json.dumps({
        "showMessage": {
            "type": "success",
            "text": f"Zdezaktywowano firmę {company.name}"
        },
        "companiesChanged": True,
        "companyUpdated": True
    })

    response.headers["HX-Trigger-After-Swap"] = json.dumps({
        "closeModal": True
    })

    return response
