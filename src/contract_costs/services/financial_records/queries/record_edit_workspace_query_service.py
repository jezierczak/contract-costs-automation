from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import Callable
from uuid import UUID


from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.amount import VatRate, AmountInputType, TaxTreatment
from contract_costs.model.contract import ContractStatus, ContractType
from contract_costs.model.financial_record import PaymentMethod, PaymentStatus, FinancialRecordStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.contract_nodes.contract_tree_query_service import ContractTreeQueryService
from contract_costs.services.contract_nodes.dto.contract_tree_query import ContractTreeQuery
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery

from contract_costs.services.contracts.query.list_contracts.list_contracts_query_service import \
    ListContractsQueryService

from contract_costs.services.financial_records.queries.dto.financial_record_edit_view import (
    FinancialRecordEditView,
    InvoiceLineEditView,
    ContractNodeView,
    PaymentEditView,
)
from contract_costs.services.financial_records.queries.dto.record_edit_workspace_query import (
    RecordEditWorkspaceQuery,
)
from contract_costs.services.financial_records.queries.dto.record_edit_workspace_view import (
    RecordEditWorkspaceView, WorkspaceContractDTO, WorkspaceValueTypeDTO,
)
from contract_costs.services.value_types.query.dto.value_type_query import ValueTypeQuery
from contract_costs.services.value_types.query.value_type_query_service import ValueTypeQueryService
from contract_costs.unit_of_work import UnitOfWork


class RecordEditWorkspaceQueryService(
    ActionHandler[RecordEditWorkspaceQuery, RecordEditWorkspaceView]
):

    def __init__(
        self,
        contract_query_service: ListContractsQueryService,
        contract_tree_query_service: ContractTreeQueryService,
        value_type_query_service: ValueTypeQueryService,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._contract_query_service = contract_query_service
        self._contract_tree_query_service = contract_tree_query_service
        self._value_type_query_service = value_type_query_service
        self._today = today

    # ============================================================
    # MAIN
    # ============================================================

    def execute(
        self,
        *,
        action: RecordEditWorkspaceQuery,
        uow: UnitOfWork,
    ) -> RecordEditWorkspaceView:

        record_view: FinancialRecordEditView | None = None
        prefill: FinancialRecordEditView | None = None
        prefill_source_reference: str | None = None

        # ===========================
        # RECORD (optional)
        # ===========================
        if action.record_id:
            record_view = self._load_record_view(action=action, record_id=action.record_id, uow=uow)

        elif action.copy_from_record_id:
            source = self._load_record_view(action=action, record_id=action.copy_from_record_id, uow=uow)
            prefill = self._as_copy(source)
            prefill_source_reference = source.reference

        # ===========================
        # ENUMS
        # ===========================
        units = [u for u in UnitOfMeasure]
        vat_rates = [v for v in VatRate]
        amount_types = [a for a in AmountInputType]
        tax_treatments = [t for t in TaxTreatment]

        payment_methods = [p for p in PaymentMethod]
        payment_statuses = [p for p in PaymentStatus]

        # ===========================
        # CONTRACTS
        # ===========================
        contracts_projects = self._contract_query_service.execute(
            action=ListContractsQuery(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                contract_type=ContractType.PROJECT,
                status=ContractStatus.ACTIVE
            ),
            uow=uow,
        )
        contracts_systems = self._contract_query_service.execute(
            action=ListContractsQuery(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                contract_type=ContractType.SYSTEM,
                status=ContractStatus.ACTIVE
            ),
            uow=uow,
        )
        contracts = contracts_projects + contracts_systems
        contracts = [
            WorkspaceContractDTO(
                contract_id=str(c.contract_id),
                code=c.code,
                name=c.name,
            )
            for c in contracts
        ]

        agreements = self._contract_query_service.execute(
            action=ListContractsQuery(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                contract_type=ContractType.AGREEMENT,
                status=ContractStatus.ACTIVE
            ),
            uow=uow,
        )
        agreements = [
            WorkspaceContractDTO(
                contract_id=str(a.contract_id),
                code=a.code,
                name=a.name,
            )
            for a in agreements
        ]

        # ===========================
        # VALUE TYPES
        # ===========================
        value_types = self._value_type_query_service.execute(
            action=ValueTypeQuery(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
            ),
            uow=uow,
        )
        value_types = [
            WorkspaceValueTypeDTO(
                id=str(v.id),
                code=v.code,
                name=v.name,
                direction=v.direction,
            )
            for v in value_types
        ]

        return RecordEditWorkspaceView(
            record=record_view,
            units=units,
            vat_rates=vat_rates,
            amount_types=amount_types,
            tax_treatments=tax_treatments,
            payment_methods=payment_methods,
            payment_statuses=payment_statuses,
            contracts=contracts,
            agreements=agreements,
            value_types=value_types,
            prefill=prefill,
            prefill_source_reference=prefill_source_reference,
        )

    # ============================================================
    # RECORD LOADING
    # ============================================================

    def _load_record_view(
        self,
        *,
        action: RecordEditWorkspaceQuery,
        record_id: UUID,
        uow: UnitOfWork,
    ) -> FinancialRecordEditView:

        record = uow.financial_records.get(
            organization_id=action.organization_id,
            record_id=record_id,
        )

        if not record:
            raise RuntimeError("Financial record not found")

        lines = uow.financial_record_lines.list_by_financial_record(
            organization_id=action.organization_id,
            financial_record_id=record.id,
        )

        buyer = uow.companies.get(
            organization_id=action.organization_id,
            company_id=record.buyer_id,
        )

        seller = uow.companies.get(
            organization_id=action.organization_id,
            company_id=record.seller_id,
        )

        payments = uow.financial_record_payments.list_by_financial_record(
            organization_id=action.organization_id,
            financial_record_id=record.id,
        )

        return self._map_record_to_edit_view(
            record=record,
            lines=lines,
            payments=payments,
            buyer=buyer,
            seller=seller,
            organization_id=action.organization_id,
            actor_user_id=action.actor_user_id,
            uow=uow,
        )

    def _as_copy(self, source: FinancialRecordEditView) -> FinancialRecordEditView:
        """
        „Dodaj podobną”: te same strony, metoda i status płatności oraz linie
        (kwoty 1:1), ale bez numeru i dokumentów; daty z dziś, termin z tym
        samym odstępem co w oryginale. Status płatności wchodzi jako płatność
        początkowa nowego rekordu: data wpłaty dziś, przy częściowej ta sama kwota.
        """
        today = self._today()
        is_paid = source.payment_status in ("paid", "partially_paid")

        due_date = None
        if source.due_date and source.invoice_date:
            due_date = today + (source.due_date - source.invoice_date)

        return replace(
            source,
            id="",
            reference="",
            invoice_date=today,
            selling_date=today,
            due_date=due_date,
            payment_status=source.payment_status,
            paid_date=today if is_paid else None,
            payments=[],
            paid_amount=source.paid_amount if source.payment_status == "partially_paid" else Decimal("0"),
            is_overpaid=False,
            documents=[],
            source_confidence=None,
            source_breakdown=None,
            lines=[replace(line, record_line_id="") for line in source.lines],
        )

    # ============================================================
    # RECORD MAPPING
    # ============================================================

    def _map_record_to_edit_view(
        self,
        *,
        record,
        lines,
        payments,
        buyer,
        seller,
        organization_id: UUID,
        actor_user_id: UUID,
        uow: UnitOfWork,
    ) -> FinancialRecordEditView:

        mapped_lines = [
            self._map_line_to_edit_view(
                line=l,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                uow=uow,
            )
            for l in lines
        ]

        total_amount = sum((l.amount.payable for l in lines), Decimal("0"))
        paid_amount = sum((p.amount for p in payments), Decimal("0"))

        mapped_payments = [
            PaymentEditView(id=str(p.id), amount=p.amount, paid_date=p.paid_date)
            for p in sorted(payments, key=lambda p: p.paid_date)
        ]

        documents = [d for d in record.documents]

        source_confidence = None
        source_breakdown = None
        if record.status in {FinancialRecordStatus.DRAFT, FinancialRecordStatus.NEW_REVENUE, FinancialRecordStatus.NEW_COST}:

            if record.documents:
                doc = record.documents[0]

                if doc.scoring:
                    source_confidence = doc.scoring.score
                    source_breakdown = doc.scoring.breakdown

        return FinancialRecordEditView(
            id=str(record.id),
            reference=record.reference,
            invoice_date=record.invoice_date,
            selling_date=record.selling_date,
            payment_method=record.payment_method.value,
            payment_status=record.payment_status.value,
            due_date=record.due_date,
            paid_date=record.paid_date,
            payments=mapped_payments,
            paid_amount=paid_amount,
            total_amount=total_amount,
            is_overpaid=paid_amount > total_amount,
            buyer_name=buyer.name if buyer else "",
            buyer_tax_number=buyer.tax_number if buyer else "",
            seller_name=seller.name if seller else "",
            seller_tax_number=seller.tax_number if seller else "",
            tags=",".join(sorted(record.tags)) if record.tags else None,
            lines=mapped_lines,
            documents=documents,
            source_confidence=source_confidence,
            source_breakdown=source_breakdown,
        )

    # ============================================================
    # LINE MAPPING
    # ============================================================

    def _map_line_to_edit_view(
        self,
        *,
        line,
        organization_id: UUID,
        actor_user_id: UUID,
        uow: UnitOfWork,
    ) -> InvoiceLineEditView:

        contract_nodes: list[ContractNodeView] = []
        agreement_nodes: list[ContractNodeView] = []



        if line.contract_id:
            tree = self._contract_tree_query_service.execute(
                action=ContractTreeQuery(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    contract_id=line.contract_id,
                ),
                uow=uow,
            )

            contract_nodes = [
                ContractNodeView(
                    id=str(n.node_id),
                    code=n.code,
                    name=n.name,
                    depth=n.depth,
                )
                for n in tree
                if n.is_active and n.is_leaf
            ]

        if line.agreement_id:
            ag_tree = self._contract_tree_query_service.execute(
                action=ContractTreeQuery(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    contract_id=line.agreement_id,
                ),
                uow=uow,
            )

            agreement_nodes = [
                ContractNodeView(
                    id=str(n.node_id),
                    code=n.code,
                    name=n.name,
                    depth=n.depth,
                )
                for n in ag_tree
                if n.is_active and n.is_leaf
            ]

        return InvoiceLineEditView(
            record_line_id=str(line.id),
            item_name=line.item_name,
            description=line.description,
            quantity=line.quantity,
            unit=line.unit.value if line.unit else "",
            amount_value=line.amount.value,
            vat_rate=line.amount.vat_rate.value,
            amount_type=line.amount.input_type.value,
            tax_treatment=line.amount.tax_treatment.value,
            contract_id=str(line.contract_id) if line.contract_id else None,
            contract_node_id=str(line.contract_node_id) if line.contract_node_id else None,
            value_type_id=str(line.value_type_id) if line.value_type_id else None,
            agreement_id=str(line.agreement_id) if line.agreement_id else None,
            agreement_node_id=str(line.agreement_node_id) if line.agreement_node_id else None,
            contract_nodes=contract_nodes,
            agreement_nodes=agreement_nodes,
        )
