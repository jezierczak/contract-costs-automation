import json
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Request, HTTPException, Form
from starlette.responses import HTMLResponse, RedirectResponse, Response

from api.dependencies import get_services

from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractType, ContractStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.companies.query.dto.company_query import CompanyQuery
from contract_costs.services.contract_nodes.dto.add_contract_node_command import AddContractNodeCommand
from contract_costs.services.contract_nodes.dto.contract_tree_query import ContractTreeQuery
from contract_costs.services.contract_nodes.dto.remove_contract_node_command import RemoveContractNodeCommand
from contract_costs.services.contract_nodes.dto.update_contract_node_command import UpdateContractNodeCommand
from contract_costs.services.contracts.apply.command.apply_contract_progerss_command import \
    ApplyContractProgressCommand, ContractNodeProgressUpdate
from contract_costs.services.contracts.apply.command.set_contract_status_command import SetContractStatusCommand
from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand
from contract_costs.services.contracts.dto.update_contract_command import UpdateContractCommand
from contract_costs.services.contracts.query.contract_details.contract_details_query_command import ContractDetailsQuery
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery

router = APIRouter()

def _render_contract_tree(
    *,
    request: Request,
    services,
    ctx,
    contract_id: UUID,
):
    tree = services.action_bus.execute(
        action=ContractTreeQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=contract_id,
        ),
        handler=services.contract_tree_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "contracts/tree_edit/_tree.html",
        {
            "request": request,
            "contract_id": contract_id,
            "nodes": tree,
            "units": [u.value for u in UnitOfMeasure],
        },
    )

@router.get("/contracts")
def contracts_page(request: Request):
    return request.app.state.templates.TemplateResponse(
        "contracts/page.html",
        {"request": request}
    )
@router.get("/contracts/table", response_class=HTMLResponse)
def contracts_list(
    request: Request,
    search: str | None = None,
    status: str | None = None,
    services=Depends(get_services),
):
    ctx = request.state.ctx
    status_enum = ContractStatus(status) if status else None
    contracts = services.action_bus.execute(
        action=ListContractsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            search=search,
            status = status_enum,
            contract_type=ContractType.PROJECT,
        ),
        handler=services.list_contracts_service,
    )



    return request.app.state.templates.TemplateResponse(
        "contracts/_table.html",
        {
            "request": request,
            "contracts": contracts,
            "search": search,
            "status": status_enum,
            "title": "Kontrakty",
        },
    )



@router.get("/contracts/new", response_class=HTMLResponse)
def contract_new(
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            include_inactive=False,
        ),
        handler=services.company_query_service,
    )
    own_companies = [c for c in companies if c.role == CompanyType.OWN]
    counterparties = [c for c in companies if c.role != CompanyType.OWN]

    return request.app.state.templates.TemplateResponse(
        "contracts/new_edit/new.html",
        {
            "request": request,
            "title": "Nowy kontrakt",
            "submit_label": "Dodaj",
            "own_companies": own_companies,
            "counterparties": counterparties,
            "action_url": "/contracts/create",
            "contract": None,
        },
    )



@router.post("/contracts/create")
def contract_create(
    request: Request,

    code: str | None = Form(None),
    name: str | None = Form(None),
    description: str | None = Form(None),

    owner_id: str | None = Form(None),
    client_id: str | None = Form(None),

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
    if not code or not code.strip():
        error = "Kod kontraktu jest wymagany"
    elif not name or not name.strip():
        error = "Nazwa kontraktu jest wymagana"
    elif not owner_id:
        error = "Wybierz firmę owner"
    else:
        error = None

    own_companies = [c for c in companies if c.role == CompanyType.OWN]
    counterparties = [c for c in companies if c.role != CompanyType.OWN]
    if error:
        return request.app.state.templates.TemplateResponse(
            "contracts/new_edit/new.html",
            {
                "request": request,
                "title": "Nowy kontrakt",
                "submit_label": "Dodaj",
                "own_companies": own_companies,
                "counterparties": counterparties,
                "action_url": "/contracts/create",
                "error": error,
                "form": {
                    "code": code or "",
                    "name": name or "",
                    "description": description or "",
                    "owner_id": owner_id or "",
                    "client_id": client_id or "",
                },
            },
        )
    owner = next((c for c in companies if str(c.id) == owner_id), None)
    client = next((c for c in companies if str(c.id) == client_id), None) if client_id else None

    if not owner:
        return request.app.state.templates.TemplateResponse(
            "contracts/new_edit/new.html",
            {
                "request": request,
                "title": "Nowy kontrakt",
                "submit_label": "Dodaj",
                "own_companies": own_companies,
                "counterparties": counterparties,
                "action_url": "/contracts/create",
                "error": "Nie znaleziono właściciela",
                "form": {
                    "code": code,
                    "name": name,
                    "description": description,
                    "owner_id": owner_id,
                    "client_id": client_id,
                }
            }
        )

    try:

        command = CreateContractCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            code=code,
            name=name,
            description=description,
            owner=owner,
            client=client,
            start_date=None,
            end_date=None,
            budget=None,
            path=None,
            status=ContractStatus.PLANNED,
            contract_type=ContractType.PROJECT,
            contract_node_input=None,
        )

        contract = services.action_bus.execute(
            action=command,
            handler=services.create_contract
        )

    except Exception as e:

        return request.app.state.templates.TemplateResponse(
            "contracts/new_edit/new.html",
            {
                "request": request,
                "title": "Nowy kontrakt",
                "submit_label": "Dodaj",
                "own_companies": own_companies,
                "counterparties": counterparties,
                "action_url": "/contracts/create",
                "error": str(e),
                "form": {
                    "code": code,
                    "name": name,
                    "description": description,
                    "owner_id": owner_id,
                    "client_id": client_id,
                }
            }
        )

    response = Response()

    response.headers["HX-Location"] = json.dumps({
        "path": f"/contracts/{contract.id}/edit",
        "target": "#content-area",
        "swap": "innerHTML"
    })

    return response

@router.get("/contracts/{contract_id}/edit", response_class=HTMLResponse)
def contract_edit(
    request: Request,
    contract_id: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    details = services.action_bus.execute(
        action=ContractDetailsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
        ),
        handler=services.contract_details_service,
    )

    if not details:
        raise HTTPException(status_code=404)

    tree = services.action_bus.execute(
        action=ContractTreeQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
        ),
        handler=services.contract_tree_query_service,
    )

    # ---------- COMPANIES ----------
    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            include_inactive=False,
        ),
        handler=services.company_query_service,
    )

    own_companies = [c for c in companies if c.role == CompanyType.OWN]
    counterparties = [c for c in companies if c.role != CompanyType.OWN]

    return request.app.state.templates.TemplateResponse(
        "contracts/new_edit/edit.html",
        {
            "request": request,
            "contract": details,
            "nodes": tree,
            "contract_id": details.contract_id,
            "own_companies": own_companies,
            "counterparties": counterparties,
            "action_url": f"/contracts/{details.contract_id}/update",
            "title": "Edytuj kontrakt",
            "submit_label": "Zapisz zmiany metadanych",
            "units": [u.value for u in UnitOfMeasure],
        },
    )

# @router.post("/contracts/{contract_id}/nodes/add")
# def contract_add_node(
#     request: Request,
#     contract_id: str,
#     parent_id: str | None = Form(None),
#     name: str = Form(...),
#     services=Depends(get_services),
# ):
#     ctx = request.state.ctx
#
#     parent_uuid = None
#     if parent_id and parent_id != "null":
#         parent_uuid = UUID(parent_id)
#
#     services.action_bus.execute(
#         action=AddContractNodeCommand(
#             organization_id=ctx.organization_id,
#             actor_user_id=ctx.user_id,
#             contract_id=UUID(contract_id),
#             parent_id=parent_uuid,
#             name=name,
#         ),
#         handler=services.add_contract_node_service,
#     )
#
#     return _render_contract_tree(
#         request=request,
#         services=services,
#         ctx=ctx,
#         contract_id=UUID(contract_id),
#     )

@router.post("/contracts/{contract_id}/nodes/remove")
def contract_remove_node(
    request: Request,
    contract_id: str,
    node_id: str = Form(...),
    services=Depends(get_services),
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=RemoveContractNodeCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
            node_id=UUID(node_id),
        ),
        handler=services.remove_contract_node_service,
    )
    return _render_contract_tree(
        request=request,
        services=services,
        ctx=ctx,
        contract_id=UUID(contract_id),
    )

@router.get("/contracts/{contract_id}/nodes/new-form")
def contract_new_node_form(
    request: Request,
    contract_id: str,
    parent_id: str | None = None,
):
    return request.app.state.templates.TemplateResponse(
        "contracts/tree_edit/_node_form_row.html",
        {
            "request": request,
            "contract_id": contract_id,
            "parent_id": parent_id,
            "units": [u.value for u in UnitOfMeasure],
        },
    )
#
@router.post("/contracts/{contract_id}/nodes/create")
def contract_create_node(
    request: Request,
    contract_id: str,
    parent_id: str | None = Form(None),
    code: str = Form(...),
    name: str = Form(...),
    quantity: str | None = Form(None),
    unit: str | None = Form(None),
    planned_budget: str | None = Form(None),
    services=Depends(get_services),
):
    ctx = request.state.ctx
    uom = UnitOfMeasure(unit)
    parent_uuid = UUID(parent_id) if parent_id else None
    services.action_bus.execute(
        action=AddContractNodeCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
            parent_id=parent_uuid,
            code=code,
            name=name,
            quantity=Decimal(quantity) if quantity else None,
            unit=uom,
            planned_budget=Decimal(planned_budget) if planned_budget else None,
        ),
        handler=services.add_contract_node_service,
    )

    return _render_contract_tree(
        request=request,
        services=services,
        ctx=ctx,
        contract_id=UUID(contract_id),
    )
#
@router.post("/contracts/{contract_id}/nodes/update")
def contract_update_node(
    request: Request,
    contract_id: str,

    node_id: str = Form(...),

    code: str = Form(...),
    name: str = Form(...),
    quantity: str | None = Form(None),
    unit: str | None = Form(None),
    planned_budget: str | None = Form(None),

    services=Depends(get_services),
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=UpdateContractNodeCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
            node_id=UUID(node_id),
            code=code,
            name=name,
            quantity=Decimal(quantity) if quantity else None,
            unit=UnitOfMeasure(unit) if unit else None,
            planned_budget=Decimal(planned_budget) if planned_budget else None,
        ),
        handler=services.update_contract_node_service,
    )

    return _render_contract_tree(
        request=request,
        services=services,
        ctx=ctx,
        contract_id=UUID(contract_id),
    )

@router.get("/contracts/{contract_id}/nodes/tree")
def contract_tree(
    request: Request,
    contract_id: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    return _render_contract_tree(
        request=request,
        services=services,
        ctx=ctx,
        contract_id=UUID(contract_id),
    )

@router.get("/contracts/{contract_id}", response_class=HTMLResponse)
def contract_view(
    request: Request,
    contract_id: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    details = services.action_bus.execute(
        action=ContractDetailsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
        ),
        handler=services.contract_details_service,
    )

    return request.app.state.templates.TemplateResponse(
        "contracts/details/page.html",
        {
            "request": request,
            "contract": details,
            "title": details.name,
            "nodes": details.nodes,
            "statuses": [s.value for s in ContractStatus],
        },
    )




@router.get("/contracts/{contract_id}/progress")
def contract_progress_view(
    request: Request,
    contract_id: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    details = services.action_bus.execute(
        action=ContractDetailsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
        ),
        handler=services.contract_details_service,
    )

    return request.app.state.templates.TemplateResponse(
        "contracts/progress/page.html",
        {
            "request": request,
            "contract": details,
        },
    )

@router.get("/contracts/{contract_id}/progress/edit")
def contract_progress_table(
    request: Request,
    contract_id: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    details = services.action_bus.execute(
        action=ContractDetailsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
        ),
        handler=services.contract_details_service,
    )

    return request.app.state.templates.TemplateResponse(
        "contracts/progress/_progress.html",
        {
            "request": request,
            "contract": details,
        },
    )


@router.post("/contracts/{contract_id}/progress/update")
async def update_progress(
    request: Request,
    contract_id: str,
    node_ids: list[str] = Form(...),
    services=Depends(get_services),
):
    ctx = request.state.ctx
    form = await request.form()

    updates = []

    for node_id in node_ids:
        value = form.get(f"progress_{node_id}").replace(",",".")

        if not value:
            continue

        updates.append(
            ContractNodeProgressUpdate(
                contract_node_id=UUID(node_id),
                progress=Decimal(value) / Decimal("100"),
                progress_date=date.today(),
            )
        )

    try:
        if updates:
            services.action_bus.execute(
                action=ApplyContractProgressCommand(
                    organization_id=ctx.organization_id,
                    actor_user_id=ctx.user_id,
                    contract_id=UUID(contract_id),
                    updates=updates,
                ),
                handler=services.apply_contract_progress_service,
            )

    except Exception as e:

        # reload danych
        details = services.action_bus.execute(
            action=ContractDetailsQuery(
                organization_id=ctx.organization_id,
                actor_user_id=ctx.user_id,
                contract_id=UUID(contract_id),
            ),
            handler=services.contract_details_service,
        )

        return request.app.state.templates.TemplateResponse(
            "contracts/progress/_progress.html",
            {
                "request": request,
                "contract": details,
                "error": str(e),
            }
        )

    # SUCCESS
    details = services.action_bus.execute(
        action=ContractDetailsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
        ),
        handler=services.contract_details_service,
    )

    return request.app.state.templates.TemplateResponse(
        "contracts/progress/_progress.html",
        {
            "request": request,
            "contract": details,
            "success": True,
        }
    )

@router.post("/contracts/{contract_id}/status")
def contract_update_status(
    request: Request,
    contract_id: str,
    status: str = Form(...),
    services=Depends(get_services),
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=SetContractStatusCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
            new_status=ContractStatus(status),
        ),
        handler=services.set_contract_status_service,
    )


    return contract_view(
        request=request,
        contract_id=contract_id,
        services=services
    )


@router.post("/contracts/{contract_id}/update")
def contract_update(
    request: Request,
    contract_id: str,

    code: str | None = Form(None),
    name: str | None = Form(None),
    description: str | None = Form(None),

    owner_id: str | None = Form(None),
    client_id: str | None = Form(None),

    services=Depends(get_services),
):
    ctx = request.state.ctx

    # ---------- VALIDATION ----------
    if not code:
        error = "Kod kontraktu jest wymagany"
    elif not name:
        error = "Nazwa kontraktu jest wymagana"
    else:
        error = None

    # ---------- LOAD COMPANIES ----------
    companies = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            include_inactive=False,
        ),
        handler=services.company_query_service,
    )

    own_companies = [c for c in companies if c.role == CompanyType.OWN]
    counterparties = [c for c in companies if c.role != CompanyType.OWN]

    owner = next((c for c in companies if str(c.id) == owner_id), None)
    client = next((c for c in companies if str(c.id) == client_id), None) if client_id else None

    # ---------- DETAILS (needed for view render) ----------
    details = services.action_bus.execute(
        action=ContractDetailsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
        ),
        handler=services.contract_details_service,
    )

    if error:
        return request.app.state.templates.TemplateResponse(
            "contracts/new_edit/edit.html",
            {
                "request": request,
                "contract": details,
                "contract_id": details.contract_id,
                "title": "Edytuj kontrakt",
                "submit_label": "Zapisz",
                "action_url": f"/contracts/{contract_id}/update",
                "own_companies": own_companies,
                "counterparties": counterparties,
                "error": error,
                "form": {
                    "code": code or "",
                    "name": name or "",
                    "description": description or "",
                    "owner_id": owner_id or "",
                    "client_id": client_id or "",
                },
            },
        )

    # ---------- UPDATE ----------
    try:
        services.action_bus.execute(
            action=UpdateContractCommand(
                organization_id=ctx.organization_id,
                actor_user_id=ctx.user_id,
                contract_id=UUID(contract_id),
                code=code,
                name=name,
                description=description,
                owner=owner,
                client=client,
            ),
            handler=services.update_contract_service,
        )

    except Exception as e:
        return request.app.state.templates.TemplateResponse(
            "contracts/new_edit/edit.html",
            {
                "request": request,
                "contract": details,
                "contract_id": details.contract_id,
                "title": "Edytuj kontrakt",
                "submit_label": "Zapisz",
                "action_url": f"/contracts/{contract_id}/update",
                "own_companies": own_companies,
                "counterparties": counterparties,
                "error": str(e),
                "form": {
                    "code": code or "",
                    "name": name or "",
                    "description": description or "",
                    "owner_id": owner_id or "",
                    "client_id": client_id or "",
                },
            },
        )

    return RedirectResponse(
        url=f"/contracts/{contract_id}",
        status_code=303,
    )