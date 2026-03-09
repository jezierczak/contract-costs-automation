from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
def home(request: Request):

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
        "dashboard.html",
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
