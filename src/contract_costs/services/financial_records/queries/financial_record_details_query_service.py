import logging
from decimal import Decimal

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_validator import \
    RecordCompletionValidator
from contract_costs.services.financial_records.queries.dto.financial_record_details_query import \
    FinancialRecordDetailsQuery
from contract_costs.services.financial_records.queries.dto.invoice_query import FinancialRecordDetailsView, InvoiceLineView
from contract_costs.unit_of_work import UnitOfWork

logger= logging.getLogger(__name__)

class FinancialRecordDetailsQueryService(
    ActionHandler[FinancialRecordDetailsQuery, FinancialRecordDetailsView]
):

    def execute(
        self,
        *,
        action: FinancialRecordDetailsQuery,
        uow: UnitOfWork,
    ) -> FinancialRecordDetailsView:

        record_repo = uow.financial_records
        record_line_repo = uow.financial_record_lines
        company_repo = uow.companies
        contract_repo = uow.contracts
        contract_node_repo = uow.contract_nodes
        value_type_repo = uow.value_types

        record = self._resolve_record(
            action=action,
            record_repo=record_repo,
        )

        lines = record_line_repo.list_by_financial_record(
            organization_id=action.organization_id,
            financial_record_id=record.id,
        )

        buyer = company_repo.get(
            organization_id=action.organization_id,
            company_id=record.buyer_id,
        )

        seller = company_repo.get(
            organization_id=action.organization_id,
            company_id=record.seller_id,
        )

        if buyer and seller:
            direction = RecordCompletionValidator.resolve_financial_record_direction(
                buyer.role,
                seller.role,
            )
        else:
            direction = None

        line_views = []
        total_net = Decimal("0")
        total_vat = Decimal("0")
        total_gross = Decimal("0")
        total_not_evidenced = Decimal("0")

        for line in lines:

            net = line.amount.net
            vat = line.amount.tax
            gross = line.amount.gross
            not_evidenced = line.amount.non_tax_cost

            total_net += net
            total_vat += vat
            total_gross += gross
            total_not_evidenced += not_evidenced

            contract = (
                contract_repo.get(
                    organization_id=action.organization_id,
                    contract_id=line.contract_id,
                )
                if line.contract_id
                else None
            )

            contract_node = (
                contract_node_repo.get(
                    organization_id=action.organization_id,
                    contract_node_id=line.contract_node_id,
                )
                if line.contract_node_id
                else None
            )

            value_type = (
                value_type_repo.get(
                    organization_id=action.organization_id,
                    value_type_id=line.value_type_id,
                )
                if line.value_type_id
                else None
            )

            line_views.append(
                InvoiceLineView(
                    item_name=line.item_name,
                    quantity=line.quantity or Decimal("0"),
                    unit=line.unit.name if line.unit else "",
                    net=net,
                    vat=vat,
                    gross=gross,
                    contract_code=contract.code if contract else None,
                    cost_node_code=contract_node.code if contract_node else None,
                    cost_type_code=value_type.code if value_type else None,
                )
            )

        return FinancialRecordDetailsView(
            id=str(record.id),
            reference=record.reference,
            status=record.status.value,
            invoice_date=record.invoice_date,
            selling_date=record.selling_date,
            buyer_name=buyer.name if buyer else "UNKNOWN",
            buyer_tax_number=buyer.tax_number if buyer else "",
            seller_name=seller.name if seller else "UNKNOWN",
            seller_tax_number=seller.tax_number if seller else "",
            lines=line_views,
            payment_method=record.payment_method.value,
            payment_status=record.payment_status.value,
            due_date=record.due_date,
            total_net=total_net,
            total_vat=total_vat,
            total_gross=total_gross,
            total_not_evidenced=total_not_evidenced,
            contract_codes=", ".join(
                {l.contract_code for l in line_views if l.contract_code}
            ),
            direction=direction.value if direction else "",
        )

    @staticmethod
    def _resolve_record(*, action, record_repo):

        if action.record_id:
            record = record_repo.get(
                organization_id=action.organization_id,
                record_id=action.record_id,
            )
            if not record:
                raise RuntimeError("Financial record not found")
            return record

        if action.reference:
            records = record_repo.get_by_reference(
                organization_id=action.organization_id,
                reference=action.reference,
            )

            if not records:
                raise RuntimeError("No financial record found")

            if len(records) > 1:
                logger.warning(
                    "Multiple financial records found for %s, returning first",
                    action.reference,
                )

            return records[0]

        raise RuntimeError("Either record_id or reference must be provided")