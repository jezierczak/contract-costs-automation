from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.responses import HTMLResponse

from api.dependencies import get_services
from contract_costs.model.company import CompanyType, Address, Contact, BankAccount
from contract_costs.services.companies.dto.create_company_command import CreateOwnerCompanyCommand, \
    CreateCounterpartyCompanyCommand
from contract_costs.services.companies.dto.deactivate_company_command import DeactivateOwnerCompanyCommand, \
    DeactivateCounterpartyCompanyCommand
from contract_costs.services.companies.dto.update_company_command import UpdateOwnerCompanyCommand, \
    UpdateCounterpartyCompanyCommand
from contract_costs.services.companies.query.dto.company_query import CompanyQuery

router = APIRouter()

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


@router.get("/companies/new", response_class=HTMLResponse)
def company_new(
    request: Request,
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
            "use_htmx": False,
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
            "use_htmx": False,
        },
    )
@router.get("/companies", response_class=HTMLResponse)
def companies_list(
    request: Request,
    search: str | None = None,
    role: str | None = None,
    inactive: int = 0,
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
        ),
        handler=services.company_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "companies/list.html",
        {
            "request": request,
            "companies": companies,
            "search": search,
            "company_types": CompanyType,
            "role": role,
            "inactive": inactive,
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

@router.get("/companies/{tax_number}", response_class=HTMLResponse)
def company_detail(
    request: Request,
    tax_number: str,
    services = Depends(get_services),
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
        raise HTTPException(status_code=404)
    company = companies[0]#query zwraca liste a poniewaz po nip mamy tylko 1 firme wiec musimy 1 element zwrócić

    return request.app.state.templates.TemplateResponse(
        "companies/detail.html",
        {
            "request": request,
            "company": company,
        },
    )


@router.get("/companies/{tax_number}/edit", response_class=HTMLResponse)
def company_edit_panel(
    request: Request,
    tax_number: str,
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
            "use_htmx": False,
        },
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

    # companies = services.action_bus.execute(
    #     action=CompanyQuery(
    #         organization_id=ctx.organization_id,
    #         actor_user_id=ctx.user_id,
    #     ),
    #     handler=services.company_query_service,
    # )

    return RedirectResponse(
        url=f"/companies/{company.tax_number}",
        status_code=303,
    )


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
    )
    if final_role == CompanyType.OWN:
        command = UpdateOwnerCompanyCommand(**base_kwargs)
    else:
        command = UpdateCounterpartyCompanyCommand(**base_kwargs)

    services.action_bus.execute(
        action=command,
        handler=services.update_company_service,
    )

    # ← reload tabeli (TAK SAMO jak create)
    # companies = services.action_bus.execute(
    #     action=CompanyQuery(
    #         organization_id=ctx.organization_id,
    #         actor_user_id=ctx.user_id,
    #     ),
    #     handler=services.company_query_service,
    # )

    return RedirectResponse(
        url=f"/companies/{tax_number}",
        status_code=303,
    )


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

    return RedirectResponse("/companies", status_code=303)