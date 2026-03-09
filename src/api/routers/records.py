import json

from fastapi import APIRouter, Depends, Request
from starlette.responses import RedirectResponse, Response, HTMLResponse
from decimal import Decimal
from uuid import UUID
from datetime import date
from api.dependencies import get_services
from contract_costs.model.amount import VatRate, AmountInputType, TaxTreatment, Amount
from contract_costs.model.business_event import BusinessEventLevel
from contract_costs.model.company import CompanyType

from contract_costs.model.financial_record import PaymentMethod, PaymentStatus, FinancialRecordStatus
from contract_costs.model.record_workspace_view import RecordWorkspaceView
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.business_event.business_event_helper import BusinessEventHelper
from contract_costs.services.companies.company_evaluate_orchestrator import EvaluateMode
from contract_costs.services.contract_nodes.dto.contract_tree_query import ContractTreeQuery
from contract_costs.services.financial_records.actions.dto.invoice_action_command import FinancialRecordActionCommand, \
    FinancialRecordAction, FinancialRecordSelector

from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.financial_records.assigment.ingest.dto.financial_record_ingest_command import \
 IngestFinancialRecordFromUICommand
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import \
    ResolvedFinancialRecordUpdate, FinancialRecordLineUpdate, RecordIngestBatch
from contract_costs.services.financial_records.queries.dto.financial_record_details_query import \
    FinancialRecordDetailsQuery
from contract_costs.services.financial_records.queries.dto.financial_record_edit_view import ContractNodeView
from contract_costs.services.financial_records.queries.dto.record_edit_workspace_query import RecordEditWorkspaceQuery
from contract_costs.services.financial_records.queries.dto.record_mainbaoard_stats_query import \
    RecordMainboardStatsQuery
from contract_costs.services.financial_records.review.dto.financial_record_review_query import \
    FinancialRecordReviewQuery
from contract_costs.services.financial_records.review.workspace_query_factory import RecordWorkspaceQueryFactory

router = APIRouter()

def d(v):
    return Decimal(v) if v else Decimal("0")

def to_date(v):
    return date.fromisoformat(v) if v else None


@router.get("/records/edit")
@router.get("/records/{record_id}/edit")
def record_edit_workspace(
    request: Request,
    record_id: str | None = None,
    services=Depends(get_services),
):
    ctx = request.state.ctx
    ctx.workspace_actions = "records/_actions_edit.html"

    # =====================
    # WORKSPACE QUERY (NEW)
    # =====================
    workspace = services.action_bus.execute(
        action=RecordEditWorkspaceQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            record_id=UUID(record_id) if record_id else None,
        ),
        handler=services.record_edit_workspace_query_service,
    )

    # =====================
    # TEMPLATE
    # =====================
    return request.app.state.templates.TemplateResponse(
        "records/edit_workspace.html",
        {
            "request": request,
            "record": workspace.record,

            "units": workspace.units,
            "vat_rates": workspace.vat_rates,
            "amount_types": workspace.amount_types,
            "tax_treatments": workspace.tax_treatments,

            "payment_methods": workspace.payment_methods,
            "payment_statuses": workspace.payment_statuses,

            "contracts": workspace.contracts,
            "agreements": workspace.agreements,
            "value_types": workspace.value_types,
        },
    )



@router.get("/records/contracts/nodes")
def contract_nodes_dropdown(
    request: Request,
    idx: str  | None = None,
    field_name: str = "contract_node_id",
    label: str = "Contract node",
    selected_node_id: str | None = None,
    services=Depends(get_services),
):
    contract_id = None

    # znajdź lines[x].contract_id
    for k, v in request.query_params.items():
        if k.endswith(".contract_id"):
            contract_id = v
            break

    if not contract_id:
        return request.app.state.templates.TemplateResponse(
            "records/_contract_nodes_select.html",
            {
                "request": request,
                "nodes": [],
                "idx": idx,
                "field_name": field_name,
                "label": label,
                "selected_node_id": selected_node_id,
            },
        )
    ctx = request.state.ctx


    tree = services.action_bus.execute(
        action=ContractTreeQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_id=UUID(contract_id),
        ),
        handler=services.contract_tree_query_service,
    )

    nodes = [
        ContractNodeView(
            id=str(n.node_id),
            code=n.code,
            name=n.name,
            depth=n.depth,
        )
        for n in tree
        if n.is_active and n.is_leaf
    ]

    return request.app.state.templates.TemplateResponse(
        "records/_contract_nodes_select.html",
        {
            "request": request,
            "nodes": nodes,
            "idx": idx,
            "field_name": field_name,
            "label": label,
            "selected_node_id": selected_node_id,
        },
    )


from collections import defaultdict

@router.post("/records/save")
async def save_record(
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx
    form = await request.form()

    data = dict(form)
    # -------------------------
    # BASIC FIELDS
    # -------------------------
    buyer_tax_number = data.get("buyer_tax_number")
    seller_tax_number = data.get("seller_tax_number")

    reference = data.get("reference")

    record_id = UUID(data["record_id"]) if data.get("record_id") else None

    with services.uow as uow:
        buyer = services.company_evaluate_orchestrator.evaluate_from_tax(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            input_tax_number=buyer_tax_number,
            role=CompanyType.BUYER,
            mode=EvaluateMode.NO_CREATE,
            uow=uow,
        )

        seller = services.company_evaluate_orchestrator.evaluate_from_tax(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            input_tax_number=seller_tax_number,
            role=CompanyType.SELLER,
            mode=EvaluateMode.NO_CREATE,
            uow=uow,
        )

    record_update = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,

        reference=reference,
        record_id=record_id,
        old_record_reference=None,

        invoice_date=to_date(data.get("invoice_date")),
        selling_date=to_date(data.get("selling_date")),
        buyer=buyer,
        seller=seller,

        payment_method=PaymentMethod(data["payment_method"]),
        due_date=to_date(data.get("due_date")),
        payment_status=PaymentStatus(data["payment_status"]),
        status=FinancialRecordStatus.DRAFT,

        paid_date=to_date(data.get("paid_date")),
        tags=data.get("tags"),
    )



    # -------------------------
    # LINES PARSE
    # -------------------------
    lines = defaultdict(dict)

    for key, value in form.multi_items():

        if not key.startswith("lines["):
            continue

        prefix, field = key.split("].")
        idx = int(prefix.replace("lines[", ""))

        lines[idx][field] = value

    lines_list = [
        line for _, line in sorted(lines.items())
    ]

    line_updates = []


    for line in lines_list:
        if line.get("contract_id") and not line.get("contract_node_id"):
            print("WARNING: contract without node", line["item_name"])
        line_updates.append(
            FinancialRecordLineUpdate(
                record_line_id=UUID(line["record_line_id"]) if line.get("record_line_id") else None,

                record_reference=reference,
                item_name=line["item_name"],
                description=line.get("description") or None,

                quantity=Decimal(line["quantity"]),
                unit=UnitOfMeasure(line["unit"]),

                amount=Amount.from_input(
                    value=d(line["amount"]),
                    input_type=AmountInputType(line["amount_type"]),
                    vat_rate=VatRate(Decimal(line["vat_rate"])),
                    tax_treatment=TaxTreatment(line["tax_treatment"]),
                ),

                contract_reference=line.get("contract_id") or None,
                contract_node_reference=line.get("contract_node_id") or None,
                value_type_reference=line.get("value_type_id") or None,
                agreement_reference=line.get("agreement_id") or None,
                agreement_node_reference=line.get("agreement_node_id") or None,
            )
        )

    # -------------------------
    # COMMAND
    # -------------------------
    batch = RecordIngestBatch(
        financial_records=[record_update],
        lines=line_updates,
    )
    try:
        result = services.action_bus.execute(
            action=IngestFinancialRecordFromUICommand(
                organization_id=ctx.organization_id,
                actor_user_id=ctx.user_id,
                batch=batch,
            ),
            handler=services.financial_record_ingest_orchestrator,
        )

        BusinessEventHelper.log(
            services=services,
            ctx=ctx,
            level=BusinessEventLevel.INFO,
            message="Rekord został poprawnie zapisany.",
            entity_type="record",
            entity_id=result,
        )

        return RedirectResponse(
            url=f"/records/{result}/edit",
            status_code=303,
        )
    except RuntimeError as e:

        BusinessEventHelper.log(
            services=services,
            ctx=ctx,
            level=BusinessEventLevel.ERROR,
            message=str(e),
            entity_type="record",
            entity_id=record_id,
        )
        response = Response(status_code=400)
        response.headers["HX-Trigger"] = json.dumps({
            "showError": str(e)
        })
        return response

# @router.get("/records/lines/{idx}/edit")
# def record_line_edit(
#     request: Request,
#     record_id:str,
#     idx: int,
#     services=Depends(get_services),
# ):
#     ctx = request.state.ctx
#
#
#     record = services.action_bus.execute(
#         action=FinancialRecordDetailsQuery(
#             organization_id=ctx.organization_id,
#             actor_user_id=ctx.user_id,
#             record_id=UUID(record_id),
#         ),
#         handler=services.financial_record_query_service,
#     )
#
#     line = record.lines[idx]
#
#     return request.app.state.templates.TemplateResponse(
#         "records/_line_edit_panel.html",
#         {
#             "request": request,
#             "l": line,
#             "idx": idx,
#             "units": [u.value for u in UnitOfMeasure],          # podasz słowniki
#             "vat_rates": [vr.value for vr in VatRate],
#             "amount_types": [at for at in AmountInputType],
#             "contracts": [],
#             "value_types": [],
#         },
#     )

# @router.get("/records/{record_id}/lines/{idx}/edit")
# def record_line_edit(request, record_id: str, idx: int, services=Depends(get_services)):
#     ctx = request.state.ctx
#
#     record = services.action_bus.execute(
#         action=FinancialRecordDetailsQuery(
#             organization_id=ctx.organization_id,
#             actor_user_id=ctx.user_id,
#             record_id=UUID(record_id),
#         ),
#         handler=services.financial_record_query_service,
#     )
#
#     return request.app.state.templates.TemplateResponse(
#         "records/_line_edit_row.html",
#         {
#             "request": request,
#             "record": record,
#             "l": record.lines[idx],
#             "idx": idx,
#             "units": [u.value for u in UnitOfMeasure],
#             "vat_rates": [v.value for v in VatRate],
#             "amount_types": [a.value for a in AmountInputType],
#             "contracts": [],
#             "value_types": [],
#         },
#     )
#
# @router.get("/records/lines/{idx}/view")
# def record_line_view(
#     request: Request,
#     idx: int,
# ):
#     return HTMLResponse("")
#
# @router.post("/records/lines/{idx}/apply")
# def record_line_apply(
#     request: Request,
#     idx: int,
# ):
#     # tu później parsing form + recalc summary
#
#     return HTMLResponse("")
@router.get("/records/lines/new-row")
def new_line_row(
    request: Request,
    idx: int,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    workspace = services.action_bus.execute(
        action=RecordEditWorkspaceQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            record_id=None,
        ),
        handler=services.record_edit_workspace_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "records/_line_edit_row.html",
        {
            "request": request,
            "idx": idx,
            "l": None,

            "units": workspace.units,
            "vat_rates": workspace.vat_rates,
            "amount_types": workspace.amount_types,
            "tax_treatments": workspace.tax_treatments,

            "contracts": workspace.contracts,
            "agreements": workspace.agreements,
            "value_types": workspace.value_types,
        },
    )
# def parse_lines_from_form(form):
#
#     lines = []
#
#     i = 0
#     while True:
#
#         key = f"lines[{i}].item_name"
#
#         # skip missing index
#         if key not in form:
#             i += 1
#             if i > 200:
#                 break
#             continue
#
#         lines.append({
#             "amount": float(form.get(f"lines[{i}].amount") or 0),
#             "vat_rate": float(form.get(f"lines[{i}].vat_rate") or 0),
#             "quantity": float(form.get(f"lines[{i}].quantity") or 0),
#         })
#
#         i += 1
#
#     return lines
#
# def calculate_summary(lines):
#
#     total_net = 0
#     total_vat = 0
#     total_gross = 0
#
#     for l in lines:
#
#         net = l["amount"] * l["quantity"]
#         vat = net * l["vat_rate"] / 100
#         gross = net + vat
#
#         total_net += net
#         total_vat += vat
#         total_gross += gross
#
#     return {
#         "net": round(total_net, 2),
#         "vat": round(total_vat, 2),
#         "gross": round(total_gross, 2),
#     }
# @router.post("/records/lines/recalc")
# async def recalc_lines(request: Request):
#
#     form = await request.form()
#
#     lines = parse_lines_from_form(form)
#
#     summary = calculate_summary(lines)
#
#     return request.app.state.templates.TemplateResponse(
#         "records/_lines_summary.html",
#         {
#             "request": request,
#             "summary": summary,
#         },
#     )

@router.get("/records")
def records_mainboard(request: Request):

    return request.app.state.templates.TemplateResponse(
        "records/mainboard.html",
        {
            "request": request,
        },
    )

@router.get("/records/mainboard/stats")
def records_mainboard_stats(request: Request, services=Depends(get_services)):
    ctx = request.state.ctx

    stats = services.action_bus.execute(
        action=RecordMainboardStatsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
        ),
        handler=services.mainboard_stats_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "records/_mainboard_cards.html",
        {
            "request": request,
            "stats": stats,
        },
    )
@router.get("/records/company")
def records_company(
    request: Request,
    company_id: str,
    year: int,
    month: int | None = None,
    services=Depends(get_services),
):

    ctx = request.state.ctx
    ctx.workspace_actions = "records/_company_records_header.html"

    from_date = date(year, month or 1, 1)

    if month:
        if month == 12:
            to_date = date(year + 1, 1, 1)
        else:
            to_date = date(year, month + 1, 1)
    else:
        to_date = date(year + 1, 1, 1)


    query = FinancialRecordReviewQuery(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,

        buyer_query={"id": company_id},
        seller_query={"id": company_id},

        from_date=from_date,
        to_date=to_date,
    )

    items = services.action_bus.execute(
        action=query,
        handler=services.review_query_service,
    )
    company_name = ""
    if items:
        company_name = items[0].buyer_name

    return request.app.state.templates.TemplateResponse(
        "records/_records_table_container.html",
        {
            "request": request,
            "records": items,
            "company_id": company_id,
            "year": year,
            "month": month,
            "company_name": company_name,
        },
    )
@router.get("/records/{view}")
def records_list(
    request: Request,
    view: RecordWorkspaceView = RecordWorkspaceView.ALL,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    query = RecordWorkspaceQueryFactory.build(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,
        view=view,
    )

    items = services.action_bus.execute(
        action=query,
        handler=services.review_query_service,
    )

    request.state.ctx.workspace_subtitle = view.value
    VIEW_LABELS = {
        RecordWorkspaceView.ASSIGN: "Przypisz nowe",
        RecordWorkspaceView.TO_ACCOUNTANT: "Do księgowej",
        RecordWorkspaceView.UNPAID_COSTS: "Niezapłacone koszty",
        RecordWorkspaceView.UNPAID_REVENUE: "Niezapłacone przychody",
    }
    request.state.ctx.workspace_subtitle = VIEW_LABELS.get(view)
    return request.app.state.templates.TemplateResponse(
        "records/list.html",
        {
            "request": request,
            "records": items,
            "view": view,
        },
    )



@router.get("/records/table/{view}")
def records_table(
    request: Request,
    view: RecordWorkspaceView,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    query = RecordWorkspaceQueryFactory.build(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,
        view=view,
    )

    records = services.action_bus.execute(
        action=query,
        handler=services.review_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "records/_table.html",
        {
            "request": request,
            "records": records,
            "view": view,
        },
    )
@router.get("/records/{record_id}/review")
def record_review_modal(
    request: Request,
    record_id: str,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    record = services.action_bus.execute(
        action=FinancialRecordDetailsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            record_id=UUID(record_id),
        ),
        handler=services.financial_record_query_service,
    )

    return request.app.state.templates.TemplateResponse(
        "records/review_modal.html",
        {
            "request": request,
            "record": record,
        },
    )

@router.post("/records/{record_id}/set-paid")
def set_paid(record_id: UUID, request: Request, services=Depends(get_services)):

    ctx = request.state.ctx

    services.action_bus.execute(
        action=FinancialRecordActionCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            selectors=[FinancialRecordSelector(record_id=record_id)],
            action=FinancialRecordAction.MARK_PAID
        ),
        handler=services.financial_record_action_service,
    )

    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message="Rekord został oznaczony jako opłacony.",
        entity_type="record",
        entity_id=record_id,
    )

    response = Response(status_code=200)
    response.headers["HX-Trigger"] = json.dumps({
        "recordsUpdated": True,
        f"recordReviewUpdated-{record_id}": True,
    })
    return response

@router.post("/records/{record_id}/delete")
def delete_record(
    record_id: UUID,
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=FinancialRecordActionCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            selectors=[FinancialRecordSelector(record_id=record_id)],
            action=FinancialRecordAction.DELETE,
        ),
        handler=services.financial_record_action_service,
    )

    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message="Rekord został usunięty.",
        entity_type="record",
        entity_id=record_id,
    )
    response = Response(status_code=200)
    response.headers["HX-Trigger"] = json.dumps({
        "recordsUpdated": True,
        f"recordReviewUpdated-{record_id}": True,
    })
    return response

@router.post("/records/{record_id}/reopen")
def reopen_record(
    record_id: UUID,
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=FinancialRecordActionCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            selectors=[FinancialRecordSelector(record_id=record_id)],
            action=FinancialRecordAction.REOPEN,
        ),
        handler=services.financial_record_action_service,
    )
    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message="Rekord został ponownie otwarty do edycji.",
        entity_type="record",
        entity_id=record_id,
    )
    response = Response(status_code=200)
    response.headers["HX-Trigger"] = json.dumps({
        "recordsUpdated": True,
        f"recordReviewUpdated-{record_id}": True,
    })
    return response

@router.post("/records/{record_id}/sent-to-accountant")
def sent_to_accountant(
    record_id: UUID,
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=FinancialRecordActionCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            selectors=[FinancialRecordSelector(record_id=record_id)],
            action=FinancialRecordAction.MARK_SENT_TO_ACCOUNTANT,
        ),
        handler=services.financial_record_action_service,
    )

    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message="Rekord wysłany do księgowej.",
        entity_type="record",
        entity_id=record_id,
    )

    response = Response(status_code=200)
    response.headers["HX-Trigger"] = json.dumps({
        "recordsUpdated": True,
        f"recordReviewUpdated-{record_id}": True,
    })
    return response

@router.post("/records/{record_id}/to-in-progress")
def to_in_progress(
    record_id: UUID,
    request: Request,
    services=Depends(get_services),
):
    ctx = request.state.ctx

    services.action_bus.execute(
        action=FinancialRecordActionCommand(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            selectors=[FinancialRecordSelector(record_id=record_id)],
            action=FinancialRecordAction.TO_IN_PROGRESS,
        ),
        handler=services.financial_record_action_service,
    )

    BusinessEventHelper.log(
        services=services,
        ctx=ctx,
        level=BusinessEventLevel.INFO,
        message="Rekord przywrócony do edycji.",
        entity_type="record",
        entity_id=record_id,
    )

    response = Response(status_code=200)
    response.headers["HX-Trigger"] = json.dumps({
        "recordsUpdated": True,
        f"recordReviewUpdated-{record_id}": True,
    })
    return response