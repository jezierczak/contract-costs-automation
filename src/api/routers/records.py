import json

from fastapi import APIRouter, Depends, Request
from starlette.responses import RedirectResponse, Response, HTMLResponse
from decimal import Decimal
from uuid import UUID
from api.dependencies import get_services
from contract_costs.model.amount import VatRate, AmountInputType, TaxTreatment, Amount
from contract_costs.model.business_event import BusinessEventLevel
from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractType, ContractStatus

from contract_costs.model.financial_record import PaymentMethod, PaymentStatus, FinancialRecordStatus
from contract_costs.model.record_workspace_view import RecordWorkspaceView
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.business_event.business_event_helper import BusinessEventHelper
from contract_costs.services.companies.company_evaluate_orchestrator import EvaluateMode
from contract_costs.services.companies.query.dto.company_query import CompanyQuery
from contract_costs.services.contract_nodes.dto.contract_tree_query import ContractTreeQuery
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery
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

from datetime import date

def _period_range(year: int, month: int | None) -> tuple[date, date]:
    start = date(year, month or 1, 1)

    if month:
        end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    else:
        end = date(year + 1, 1, 1)

    return start, end


def _fetch_company_records(
    *,
    ctx,
    services,
    company_id: str,
    year: int,
    month: int | None,
    owner_company_id: str | None = None,

    any_value: str | None = None,
    direction: str | None = None,
    contract_code: str | None = None,
    unpaid: str | None = None,
    tax_deductible: str | None = None,
    non_deductible: str | None = None,
    non_cash_cost: str | None = None,
):
    from_date, to_date = _period_range(year, month)

    # ===============================
    # BASE COMPANY FILTER
    # ===============================
    if owner_company_id:
        buyer_query = {"id": [company_id, owner_company_id]}
        seller_query = {"id": [owner_company_id, company_id]}
    else:
        buyer_query = {"id": company_id}
        seller_query = {"id": company_id}

    # ===============================
    # SEARCH (any)
    # ===============================
    if any_value:
        buyer_query = {**buyer_query, "any": any_value}
        seller_query = {**seller_query, "any": any_value}

    direction_enum = None
    if direction:
        direction_enum = ValueDirection(direction)

    payment_status = None
    if unpaid:
        payment_status = PaymentStatus.UNPAID
    # ===============================
    # BUILD QUERY
    # ===============================
    query = FinancialRecordReviewQuery(
        organization_id=ctx.organization_id,
        actor_user_id=ctx.user_id,

        buyer_query=buyer_query,
        seller_query=seller_query,

        from_date=from_date,
        to_date=to_date,

        contract_codes=[contract_code] if contract_code else None,
        direction=direction_enum,
        payment_statuses=[payment_status] if payment_status else None,
    )

    # ===============================
    # FUTURE FILTERS (placeholder)
    # ===============================
    # TODO: jak dodasz do query:
    # if tax_deductible:
    #     ...
    # if non_deductible:
    #     ...
    # if non_cash_cost:
    #     ...

    # ===============================
    # EXECUTE
    # ===============================
    return services.action_bus.execute(
        action=query,
        handler=services.review_query_service,
    )

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

    buyer_tax_number = request.query_params.get("buyer_tax_number")
    seller_tax_number = request.query_params.get("seller_tax_number")

    prefill_company_buyer = None
    prefill_company_seller = None
    default_own_company = None

    if buyer_tax_number:
        prefill_company_buyers = services.action_bus.execute(
            action=CompanyQuery(
                organization_id=ctx.organization_id,
                actor_user_id=ctx.user_id,
                tax_number=buyer_tax_number,
            ),
            handler=services.company_query_service,
        )
        if prefill_company_buyers:
            prefill_company_buyer = prefill_company_buyers[0]

    if seller_tax_number:
        prefill_company_sellers = services.action_bus.execute(
        action=CompanyQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            tax_number=seller_tax_number,
        ),
        handler=services.company_query_service,
    )
        if prefill_company_sellers:
            prefill_company_seller = prefill_company_sellers[0]

    if prefill_company_buyer or prefill_company_seller:
        owns = services.action_bus.execute(
            action=CompanyQuery(
                organization_id=ctx.organization_id,
                actor_user_id=ctx.user_id,
                own_only=True
            ),
            handler=services.company_query_service,
        )
        default_own_company = owns[0] if owns else None

    if default_own_company:
        if prefill_company_buyer and not prefill_company_seller:
            prefill_company_seller = default_own_company
        elif prefill_company_seller and not prefill_company_buyer:
            prefill_company_buyer = default_own_company

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
        "records/edit/edit_workspace.html",
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

            "prefill_company_buyer": prefill_company_buyer,
            "prefill_company_seller": prefill_company_seller,
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
        "records/edit/_line_edit_row.html",
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
        }
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
        "records/page.html",
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
        "records/_dashboard_cards.html",
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

    contracts = services.action_bus.execute(
        action=ListContractsQuery(
            organization_id=ctx.organization_id,
            actor_user_id=ctx.user_id,
            contract_type=ContractType.PROJECT,
            status=ContractStatus.ACTIVE,
        ),
        handler=services.list_contracts_service,
    )

    return request.app.state.templates.TemplateResponse(
        "records/company/page.html",
        {
            "request": request,
            "company_id": company_id,
            "year": year,
            "month": month,
            "contracts": contracts,
        },
    )

@router.get("/records/table")
def records_table(
    request: Request,
    company_id: str,
    year: int,
    owner_company_id: UUID | None = None,
    month: int | None = None,
    services=Depends(get_services),
):
    params = request.query_params

    any_value = params.get("any")
    direction = params.get("direction")
    contract_code = params.get("contract_code")

    unpaid = params.get("unpaid")
    tax_deductible = params.get("TAX_DEDUCTIBLE")
    non_deductible = params.get("NON_DEDUCTIBLE")
    non_cash_cost = params.get("NON_CASH_COST")

    ctx = request.state.ctx

    items = _fetch_company_records(
        ctx=ctx,
        services=services,
        company_id=company_id,
        year=year,
        month=month,
        owner_company_id=owner_company_id,

        any_value = any_value,
        direction = direction,
        contract_code = contract_code,
        unpaid = unpaid,
        tax_deductible = tax_deductible,
        non_deductible = non_deductible,
        non_cash_cost = non_cash_cost
    )

    return request.app.state.templates.TemplateResponse(
        "records/list_records/_table.html",
        {
            "request": request,
            "records": items,
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

    VIEW_LABELS = {
        RecordWorkspaceView.ASSIGN: "Przypisz nowe",
        RecordWorkspaceView.TO_ACCOUNTANT: "Do księgowej",
        RecordWorkspaceView.UNPAID_COSTS: "Niezapłacone koszty",
        RecordWorkspaceView.UNPAID_REVENUE: "Niezapłacone przychody",
    }
    request.state.ctx.workspace_subtitle = VIEW_LABELS.get(view)
    return request.app.state.templates.TemplateResponse(
        "records/list_records/list.html",
        {
            "request": request,
            "records": items,
            "view": view,
             "view_label": VIEW_LABELS.get(view)
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
        "records/list_records/_table.html",
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