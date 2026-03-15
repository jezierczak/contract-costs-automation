from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies import get_services
from contract_costs.services.company_dashboard.dto.company_dashboard_query import CompanyDashboardQuery
from contract_costs.services.company_dashboard.dto.company_fixerd_costs_query import CompanyFixedCostsQuery
from contract_costs.services.company_dashboard.dto.company_month_breakdown_query import CompanyBreakdownQuery

router = APIRouter()


@router.get("/own-company-finances")
def own_company_dashboard(
    request: Request,
    company_id: str | None = None,
    year: int | None = None,
    services=Depends(get_services),
):

    ctx = request.state.ctx

    company_uuid = UUID(company_id) if company_id else None

    action = CompanyDashboardQuery(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,
        company_id=company_uuid,
        year=year,
    )

    dashboard = services.action_bus.execute(
        action=action,
        handler=services.company_dashboard_query_service,
    )

    template_data = {
        "request": request,
        "dashboard": dashboard,
        "selected_company_id": dashboard.selected_company_id,
        "owner_companies": dashboard.owner_companies,
        "current_year": datetime.now().year
    }

    # HTMX → tylko content
    # if request.headers.get("HX-Request"):
    #     return request.app.state.templates.TemplateResponse(
    #         "own_company_dashboard/_dashboard_content.html",
    #         template_data,
    #     )

    # normalny request → pełny widok
    return request.app.state.templates.TemplateResponse(
        "own_company_dashboard/page.html",
        template_data,
    )

@router.get("/own-company-finances/month-breakdown")
def month_breakdown(
    request: Request,
    company_id: str,
    year: int,
    month: int | None = None,
    services=Depends(get_services),
):

    ctx = request.state.ctx

    action = CompanyBreakdownQuery(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,
        company_id=UUID(company_id),
        year=year,
        month=month,
    )

    data = services.action_bus.execute(
        action=action,
        handler=services.company_month_breakdown_service,
    )

    return request.app.state.templates.TemplateResponse(
        "own_company_dashboard/_breakdown_modal.html",
        {
            "request": request,
            "year": action.year,
            "month": action.month,

            "costs": data.costs,
            "revenues": data.revenues,
            "cost_total": data.cost_total,
            "revenue_total": data.revenue_total,
        }
    )

@router.get(
    "/own-company-finances/fixed-costs"

)
def fixed_costs_modal(
    request: Request,
    company_id: str,
    year: int,
    month: int | None = None,
    services=Depends(get_services),
):

    ctx = request.state.ctx

    data = services.action_bus.execute(
        action=CompanyFixedCostsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            company_id=UUID(company_id),
            year=year,
            month=month,
        ),
        handler=services.company_fixed_costs_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "own_company_dashboard/fixed_costs_modal.html",
        {
            "request": request,
            "data": data,
        },
    )