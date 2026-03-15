import logging
import threading
from uuid import UUID

from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from contract_costs.cli.context import get_services

from pathlib import Path as FilePath

from contract_costs.common.time import utc_now
from contract_costs.services.identity.auth.session.dto.clean_up_expired_sessions_command import \
    CleanupExpiredSessionsCommand


from api.context.request_context import RequestContext
from api.routers import auth, companies, dashboard, contracts,documents,records,business_events,value_types, own_company_dashboard


logger = logging.getLogger(__name__)
app = FastAPI()

services = get_services()

app.state.services = services


@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.on_event("startup")
def cleanup_sessions():

    services.action_bus.execute(
        action=CleanupExpiredSessionsCommand(),
        handler=services.cleanup_expired_sessions_service,
    )

@app.on_event("startup")
def start_workers():

    worker = services.document_parse_worker

    thread = threading.Thread(
        target=worker.run,
        name="document-worker",
    )

    thread.start()

@app.on_event("shutdown")
def shutdown_event():
    worker = services.document_parse_worker

    worker.stop()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # tutaj logger.exception(...)
    return HTMLResponse(
        "<h2>Wystąpił błąd serwera.</h2>",
        status_code=500,
    )

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    request.state.ctx = RequestContext()

    core_services = request.app.state.services
    session_id = request.cookies.get("session_id")

    if session_id:
        try:
        #     print("pre session")
            with core_services.uow as uow:
                session = uow.sessions.get(UUID(session_id))
            # print("SESSION:", session)
        except Exception as a:
            logger.exception("SESSION REMOTE ERROR: %s",a)
            session = None

        if session:
            now = utc_now()
            if session.expires_at < now.replace(tzinfo=None):
                with core_services.uow as uow:
                    uow.sessions.delete(session.id)
            else:
                request.state.ctx.user_id = session.user_id
                request.state.ctx.organization_id = session.organization_id
                with core_services.uow as uow:
                    request.state.ctx.user = uow.users.get(session.user_id)
                    request.state.ctx.organization= uow.organizations.get(session.organization_id)
                    request.state.ctx.membership = uow.organization_users.get_by_org_and_user(
                                organization_id=session.organization_id,
                                user_id=session.user_id,
                                )
                # request.state.current_user = uow.users.get(session.user_id)
                # request.state.current_org = uow.organizations.get(session.organization_id)


    response = await call_next(request)
    return response


BASE_DIR = FilePath(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.state.templates = templates

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(dashboard.router)

app.include_router(contracts.router)

app.include_router(documents.router)

app.include_router(records.router)

app.include_router(business_events.router)

app.include_router(value_types.router)

app.include_router(own_company_dashboard.router)