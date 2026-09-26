from fastapi import APIRouter, Request

from contract_costs.services.company_dashboard.financials.company_financials_calculator import MONTH_NAMES
from contract_costs.services.dashboard.dto.dashboard_query import DashboardQuery

router = APIRouter()


@router.get("/")
def home(request: Request):
    return _render_dashboard(request, template="dashboard.html")


@router.get("/dashboard")
def dashboard(request: Request):
    # kliknięcie w menu (htmx) podmienia tylko obszar treści;
    # odświeżenie strony pod /dashboard dostaje pełny layout
    is_htmx = request.headers.get("HX-Request") == "true"
    return _render_dashboard(
        request,
        template="dashboard/_content.html" if is_htmx else "dashboard.html",
    )


def _render_dashboard(request: Request, *, template: str):

    if not request.state.ctx.user_id:
        return request.app.state.templates.TemplateResponse(
            "auth/login.html",
            {"request": request},
        )

    services = request.app.state.services

    ctx = request.state.ctx

    with services.uow as uow:
        has_owner = uow.companies.exists_owner(
            ctx.organization_id
        )

    dashboard = None
    if has_owner:
        dashboard = services.action_bus.execute(
            action=DashboardQuery(
                organization_id=ctx.organization_id,
                actor_user_id=ctx.user_id,
            ),
            handler=services.dashboard_query_service,
        )

    return request.app.state.templates.TemplateResponse(
        template,
        {
            "request": request,
            "has_owner": has_owner,
            "dashboard": dashboard,
            "last_month_label": (
                f"{MONTH_NAMES[dashboard.last_month]} {dashboard.last_month_year}" if dashboard else ""
            ),
            "title": "🚀 Pierwszy krok",
            "subtitle": "Dodaj swoją firmę",
            "action_url": "/companies/create-own",
            "submit_label": "Dodaj firmę",
            "show_role": False,
            "company": None,
            "use_htmx": False,
        },
    )
