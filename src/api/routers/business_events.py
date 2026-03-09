from fastapi import APIRouter
from starlette.requests import Request


from contract_costs.services.business_event.dto.list_business_events_query_command import ListBusinessEventsQueryCommand

router = APIRouter()


@router.get("/business-events/latest")
def latest_event(
        request: Request
    ):
    ctx = request.state.ctx
    services = request.app.state.services

    events = services.action_bus.execute(
        action=ListBusinessEventsQueryCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            limit=1,
        ),
        handler=services.list_business_events_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "business_events/_latest.html",
        {
            "request": request,
            "events": events,
        },
    )

@router.get("/business-events/modal")
def business_events_table(request: Request):

    ctx = request.state.ctx
    services = request.app.state.services

    events = services.action_bus.execute(
        action=ListBusinessEventsQueryCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            limit=30,
        ),
        handler=services.list_business_events_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "business_events/modal.html",
        {
            "request": request,
            "events": events,
        },
    )