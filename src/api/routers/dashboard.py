from fastapi import APIRouter, Request

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

    with services.uow as uow:
        has_owner = uow.companies.exists_owner(
            request.state.ctx.organization_id
        )

    return request.app.state.templates.TemplateResponse(
        template,
        {
            "request": request,
            "has_owner": has_owner,
            "title": "🚀 Pierwszy krok",
            "subtitle": "Dodaj swoją firmę",
            "action_url": "/companies/create-own",
            "submit_label": "Dodaj firmę",
            "show_role": False,
            "company": None,
            "use_htmx": False,
        },
    )
