import logging
from decimal import Decimal
from uuid import UUID

from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_validator import \
    RecordCompletionValidator
from contract_costs.services.financial_records.queries.dto.invoice_query import FinancialRecordDetailsView, InvoiceLineView

logger= logging.getLogger(__name__)

class FinancialRecordDetailsQueryService:

    def __init__(
        self,
        record_repo: FinancialRecordRepository,
        record_line_repo: FinancialRecordLineRepository,
        company_repo: CompanyRepository,
        contract_repo: ContractRepository,
        contract_node_repo: ContractNodeRepository,
        value_type_repo: ValueTypeRepository,
    ) -> None:
        self._record_repo = record_repo
        self._record_line_repo = record_line_repo
        self._company_repo = company_repo
        self._contract_repo = contract_repo
        self._contract_node_repo = contract_node_repo
        self._value_type_repo = value_type_repo

    def get_by_reference(self,
                         *,
                         organization_id:UUID,
                         reference: str) -> FinancialRecordDetailsView:
        records = self._record_repo.get_by_reference(organization_id=organization_id, reference=reference)

        if not records:
            raise RuntimeError(f"No financial record found for {reference}")

        if len(records) > 1:
            logger.warning(
                f"Multiple financial records found for {reference}. Found: {len(records)}: ")
            for record in records:
                logger.warning(f"Financial record id: {record.id}")
            logger.warning(
                f"Please specify financial record ID. Provided first match!"
            )

        return self.get_invoice(organization_id,records[0].id)

    def get_invoice(self, organization_id, record_id: UUID) -> FinancialRecordDetailsView:
        record=self._record_repo.get(organization_id=organization_id, record_id=record_id)

        if not record:
            raise RuntimeError(f"Financial record not found: {record_id}")

        lines = self._record_line_repo.list_by_financial_record(organization_id=organization_id,financial_record_id=record.id)

        buyer = self._company_repo.get(organization_id=organization_id,company_id=record.buyer_id)
        seller = self._company_repo.get(organization_id=organization_id,company_id=record.seller_id)

        if buyer and seller:
            direction = RecordCompletionValidator.resolve_financial_record_direction(buyer.role, seller.role)
        else: direction = None

        line_views: list[InvoiceLineView] = []

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
                self._contract_repo.get(organization_id=organization_id,contract_id=line.contract_id)
                if line.contract_id else None
            )

            cost_node = (
                self._contract_node_repo.get(organization_id=organization_id,contract_node_id=line.contract_node_id)
                if line.contract_node_id else None
            )

            cost_type = (
                self._value_type_repo.get(organization_id=organization_id,value_type_id=line.value_type_id)
                if line.value_type_id else None
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
                    cost_node_code=cost_node.code if cost_node else None,
                    cost_type_code=cost_type.code if cost_type else None,
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
            contract_codes=", ".join({line.contract_code for line in line_views  if line.contract_code is not None}),
            direction=direction.value if direction else "",
        )
