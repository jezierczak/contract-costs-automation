from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.requests import Request
from starlette.responses import Response

from api.dependencies import get_services
from contract_costs.model.business_event import BusinessEventLevel
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.business_event.business_event_helper import BusinessEventHelper
from contract_costs.services.value_types.apply.commands.activate_value_type_command import ActivateValueTypeCommand
from contract_costs.services.value_types.apply.commands.deactivate_value_type_command import DeactivateValueTypeCommand
from contract_costs.services.value_types.apply.commands.update_value_type_command import UpdateValueTypeCommand
from contract_costs.services.value_types.dto.create_value_type_command import CreateValueTypeCommand
from contract_costs.services.value_types.query.dto.value_type_query import ValueTypeQuery

router = APIRouter()

@router.get("/value_types")
def value_types_list(
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    items = services.action_bus.execute(
        action=ValueTypeQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
        ),
        handler=services.value_type_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "value_types/page.html",
        {
            "request": request,
            "items": items,
        },
    )

@router.get("/value_types/{reference}/review")
def value_type_review(
    reference: str,
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    # ====================================
    # Detect reference type
    # ====================================
    value_type_id = None
    value_type_code = None

    try:
        value_type_id = UUID(reference)
    except ValueError:
        value_type_code = reference

    items = services.action_bus.execute(
        action=ValueTypeQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            code=value_type_code,
            id=value_type_id,
            include_inactive=True
        ),
        handler=services.value_type_query_service,
    )
    if items:
        item = items[0]
    else:

        response = Response(status_code=400)
        response.headers["HX-Trigger"] = f'{{"showError":"Nie znaleziono kategorii finansowej!"}}'
        return response

    return request.app.state.templates.TemplateResponse(
        "value_types/review_modal.html",
        {
            "request": request,
            "item": item,
        },
    )

@router.get("/value_types/edit")
@router.get("/value_types/{value_type_code}/edit")
def value_type_edit(
    request: Request,
    value_type_code: str | None = None,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    item = None

    if value_type_code:
        items = services.action_bus.execute(
            action=ValueTypeQuery(
                organization_id=ctx.organization_id,
                actor_user_id=ctx.user_id,
                code=value_type_code,
                include_inactive=True
            ),
            handler=services.value_type_query_service,
        )

        if items:
            item = items[0]


    return request.app.state.templates.TemplateResponse(
        "value_types/form_modal.html",
        {
            "request": request,
            "item": item,
            "directions": [d.value for d in ValueDirection],
        },
    )

@router.get("/value_types/table")
def value_types_table(
    request: Request,
    include_inactive: bool = False,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    items = services.action_bus.execute(
        action=ValueTypeQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            include_inactive=include_inactive,
        ),
        handler=services.value_type_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "value_types/_table.html",
        {
            "request": request,
            "items": items,
            "include_inactive": include_inactive,
        },
    )

@router.post("/value_types/{value_type_id}/delete")
def value_type_delete(
    value_type_id: UUID,
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=DeactivateValueTypeCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            value_type_id=value_type_id,
        ),
        handler=services.deactivate_value_type_service,
    )
    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message="Usunięto kategorię finansową",
        entity_type="value_type",
        entity_id=value_type_id,
    )
    response = Response(status_code=200)

    # 🔥 refresh list
    response.headers["HX-Trigger"] = "valueTypesUpdated"

    return response

@router.post("/value_types/{value_type_id}/activate")
def value_type_activate(
    value_type_id: UUID,
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=ActivateValueTypeCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            value_type_id=value_type_id,
        ),
        handler=services.activate_value_type_service,
    )
    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message="Aktywowano ponownie kategorie finansową",
        entity_type="value_type",
        entity_id=value_type_id,
    )
    response = Response(status_code=200)

    # 🔥 refresh list
    response.headers["HX-Trigger"] = "valueTypesUpdated"

    return response

@router.post("/value_types/save")
async def value_type_save(request: Request, services=Depends(get_services)):
    ctx = request.state.ctx
    form = await request.form()
    data = dict(form)

    value_type_id = data.get("id") or None

    try:

        if value_type_id:
            print(value_type_id)

            services.action_bus.execute(
                action=UpdateValueTypeCommand(
                    organization_id=ctx.organization_id,
                    actor_user_id=ctx.user_id,
                    value_type_id=UUID(value_type_id),
                    code=data["code"],
                    name=data["name"],
                    description=data.get("description") or None,
                    direction=ValueDirection(data["direction"]),
                ),
                handler=services.update_value_type_service,
            )

            BusinessEventHelper.log(
                services=services,
                ctx=ctx,
                level=BusinessEventLevel.INFO,
                message=f"Zaktualizowano Value Type: {data['code']}",
                entity_type="value_type",
                entity_id=UUID(value_type_id),
            )

        else:

            new_id = services.action_bus.execute(
                action=CreateValueTypeCommand(
                    organization_id=ctx.organization_id,
                    actor_user_id=ctx.user_id,
                    code=data["code"],
                    name=data["name"],
                    description=data.get("description") or None,
                    direction=ValueDirection(data["direction"]),
                ),
                handler=services.create_value_type,
            )

            BusinessEventHelper.log(
                services=services,
                ctx=ctx,
                level=BusinessEventLevel.INFO,
                message=f"Utworzono Value Type: {data['code']}",
                entity_type="value_type",
                entity_id=new_id,
            )

        response = Response(status_code=200)
        response.headers["HX-Trigger"] = "valueTypesUpdated"
        return response

    except Exception as e:

        BusinessEventHelper.log(
            services=services,
            ctx=ctx,
            level=BusinessEventLevel.ERROR,
            message=str(e),
            entity_type="value_type",
            entity_id=UUID(value_type_id) if value_type_id else None,
        )

        response = Response(status_code=400)
        response.headers["HX-Trigger"] = f'{{"showError":"{str(e)}"}}'
        return response