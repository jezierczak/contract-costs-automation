from decimal import Decimal

from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.services.invoices.dto.invoice_query import InvoiceDetailsView, InvoiceLineView


class InvoiceDetailsQueryService:

    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        invoice_line_repo: InvoiceLineRepository,
        company_repo: CompanyRepository,
        contract_repo: ContractRepository,
        cost_node_repo: CostNodeRepository,
        cost_type_repo: CostTypeRepository,
    ) -> None:
        self._invoice_repo = invoice_repo
        self._invoice_line_repo = invoice_line_repo
        self._company_repo = company_repo
        self._contract_repo = contract_repo
        self._cost_node_repo = cost_node_repo
        self._cost_type_repo = cost_type_repo

    def get_by_invoice_number(self, invoice_number: str) -> InvoiceDetailsView:
        invoice = self._invoice_repo.get_by_invoice_number(invoice_number)
        if not invoice:
            raise RuntimeError(f"Invoice not found: {invoice_number}")

        lines = self._invoice_line_repo.list_by_invoice(invoice.id)

        buyer = self._company_repo.get(invoice.buyer_id)
        seller = self._company_repo.get(invoice.seller_id)

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
                self._contract_repo.get(line.contract_id)
                if line.contract_id else None
            )

            cost_node = (
                self._cost_node_repo.get(line.cost_node_id)
                if line.cost_node_id else None
            )

            cost_type = (
                self._cost_type_repo.get(line.cost_type_id)
                if line.cost_type_id else None
            )

            line_views.append(
                InvoiceLineView(
                    item_name=line.item_name,
                    quantity=line.quantity,
                    unit=line.unit.name,

                    net=net,
                    vat=vat,
                    gross=gross,

                    contract_code=contract.code if contract else None,
                    cost_node_code=cost_node.code if cost_node else None,
                    cost_type_code=cost_type.code if cost_type else None,
                )
            )

        return InvoiceDetailsView(
            invoice_number=invoice.invoice_number,
            status=invoice.status.value,
            invoice_date=invoice.invoice_date,
            selling_date=invoice.selling_date,

            buyer_name=buyer.name if buyer else "UNKNOWN",
            buyer_tax_number=buyer.tax_number if buyer else "",

            seller_name=seller.name if seller else "UNKNOWN",
            seller_tax_number=seller.tax_number if seller else "",

            lines=line_views,
            payment_method=invoice.payment_method.value,
            payment_status=invoice.payment_status.value,
            due_date=invoice.due_date,

            total_net=total_net,
            total_vat=total_vat,
            total_gross=total_gross,
            total_not_evidenced=total_not_evidenced,
        )
