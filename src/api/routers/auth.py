from uuid import UUID
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi import APIRouter, Depends, Form,Request
from contract_costs.services.identity.add.dto.create_organization_command import CreateOrganizationCommand
from api.dependencies import get_services
from passlib.context import CryptContext

from contract_costs.services.identity.auth.session.dto.create_session_command import CreateSessionCommand
from contract_costs.services.identity.auth.session.dto.logout_command import LogoutCommand
from contract_costs.services.identity.auth.session.dto.update_session_organization_command import \
    UpdateSessionOrganizationCommand
from contract_costs.services.identity.exceptions import UserNotFound, PermissionDenied, UserInactive, \
    IdentityServiceError, UserAlreadyExists, OrganizationAlreadyExists
from contract_costs.services.identity.auth.dto.authenticate_user_command import AuthenticateUserCommand
from contract_costs.services.identity.query.dto.list_user_organizations_query import ListUserOrganizationsQuery

router = APIRouter()
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)
@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):

    return request.app.state.templates.TemplateResponse(
        "auth/register.html",
        {"request": request},
    )
@router.post("/register", response_class=HTMLResponse)
def register(

    # request: Request,
    organization_code: str = Form(...),
    organization_name: str = Form(...),
    login: str = Form(...),
    full_name: str | None = Form(None),
    email: str | None = Form(None),

    password: str = Form(...),
    password_repeat: str = Form(...),

    services=Depends(get_services),
):
    if password != password_repeat:
        return HTMLResponse(
            "<p class='text-red-600'>Hasła nie są takie same</p>"

        )
    password_hash = pwd_context.hash(password)
    command = CreateOrganizationCommand(
        organization_code=organization_code,
        organization_name=organization_name,
        owner_login=login,
        owner_email=email,
        owner_full_name=full_name,
        created_by_user_id=None,
        owner_password_hash=password_hash,
    )
    try:
        org_id, user_id = services.action_bus.execute(action=command,handler = services.create_organization_with_owner)
        session_id = services.action_bus.execute(
            action=CreateSessionCommand(
                actor_user_id=user_id,
                organization_id=org_id,  # jeśli masz
            ),
            handler=services.create_session_service,
        )
    except OrganizationAlreadyExists:
        return HTMLResponse(
            "<p style='color:red;'>Organizacja już istnieje</p>"
        )

    except UserAlreadyExists:
        return HTMLResponse(
            "<p style='color:red;'>Login już istnieje</p>"
        )
    response = Response(headers={"HX-Redirect": "/"})

    response.set_cookie(
        key="session_id",
        value=str(session_id),
        httponly=True,
        samesite="lax",
    )

    return response

@router.post("/login", response_class=RedirectResponse)
def login(
    login: str = Form(...),
    password: str = Form(...),
    services = Depends(get_services),
):
    command = AuthenticateUserCommand(
        login=login,
        password=password,
    )
    try:
        user_id = services.action_bus.execute(
            action=command,
            handler=services.authenticate_user_service,
        )
    except UserNotFound:
        return HTMLResponse("<p style='color:red;'>Nieprawidłowy login</p>")
    except PermissionDenied:
        return HTMLResponse("<p style='color:red;'>Nieprawidłowe hasło</p>")
    except UserInactive:
        return HTMLResponse("<p style='color:red;'>Użytkownik został zdezaktywowany</p>")
    except IdentityServiceError:
        return HTMLResponse("<p style='color:red;'>Błąd identyfikacji</p>")
    # if not pwd_context.verify(password, user.password_hash):
    #     return HTMLResponse("<p style='color:red;'>Nieprawidłowe hasło</p>")
    # 2. Create session

    orgs = services.action_bus.execute(
        action=ListUserOrganizationsQuery(actor_user_id=user_id),
        handler=services.list_user_organizations_user_service,
    )
    if len(orgs) == 1:
        org_id = orgs[0].id
        session_id = services.action_bus.execute(
            action=CreateSessionCommand(
                actor_user_id=user_id,
                organization_id=org_id,
            ),
            handler=services.create_session_service,
        )
        response = RedirectResponse("/", status_code=303)

    else:
        # redirect to organization choice
        session_id = services.action_bus.execute(
            action=CreateSessionCommand(
                actor_user_id=user_id,
                organization_id=None,
            ),
            handler=services.create_session_service,
        )
        response = RedirectResponse("/select-organization", status_code=303)
    response.set_cookie(
        key="session_id",
        value=str(session_id),
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/logout")
def logout(request: Request, services = Depends(get_services)):

    session_id = request.cookies.get("session_id")

    if session_id:
        command = LogoutCommand(session_id=UUID(session_id))

        services.action_bus.execute(
            action=command,
            handler=services.logout_service,
        )

    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("session_id")

    return response


@router.get("/select-organization", response_class=HTMLResponse)
def select_organization_page(
    request: Request,
    services=Depends(get_services),
):
    if not request.state.user_id:
        return RedirectResponse("/", status_code=303)

    orgs = services.action_bus.execute(
        action=ListUserOrganizationsQuery(
            actor_user_id=request.state.user_id
        ),
        handler=services.list_user_organizations_user_service,
    )

    return request.app.state.templates.TemplateResponse(
        "auth/select_organization.html",
        {
            "request": request,
            "organizations": orgs,
        },
    )

@router.post("/select-organization")
def select_organization(
    request: Request,
    organization_id: UUID = Form(...),
    services=Depends(get_services),
):
    session_id = request.cookies.get("session_id")

    if not session_id:
        return RedirectResponse("/", status_code=303)

    services.action_bus.execute(
        action=UpdateSessionOrganizationCommand(
            session_id=UUID(session_id),
            organization_id=organization_id,
        ),
        handler=services.update_session_organization_service,
    )

    return RedirectResponse("/", status_code=303)
