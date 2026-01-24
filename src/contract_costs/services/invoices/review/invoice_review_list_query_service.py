from decimal import Decimal
from uuid import UUID

from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.repository.invoice_repository import InvoiceRepository

from contract_costs.services.invoices.assigment.ingest.completion_validator.invoice_completion_validator import \
    InvoiceCompletionValidator

from contract_costs.services.invoices.review.dto.invoice_review_item_view import InvoiceReviewItemView
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery


class InvoiceReviewListQueryService:

    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        company_repo: CompanyRepository,
        invoice_line_repo: InvoiceLineRepository,
        contract_repo: ContractRepository,
    ) -> None:
        self._invoice_repo = invoice_repo
        self._company_repo = company_repo
        self._invoice_line_repo = invoice_line_repo
        self._contract_repo = contract_repo

    def list_for_review(self, review_query: InvoiceReviewQuery) -> list[InvoiceReviewItemView]:

        invoices = self._invoice_repo.list_for_review(review_query)

        result = []

        contracts: dict[UUID, str] = {item.id:item.code for item in self._contract_repo.list()}

        for inv in invoices:
            buyer = self._company_repo.get(inv.buyer_id)
            seller = self._company_repo.get(inv.seller_id)

            if buyer and seller:
                direction= InvoiceCompletionValidator.resolve_invoice_direction(buyer.role, seller.role)
            else: direction = None
            lines = self._invoice_line_repo.list_by_invoice(inv.id)
            total_net = Decimal("0")
            total_vat = Decimal("0")
            total_gross = Decimal("0")
            total_not_evidenced = Decimal("0")

            contract_codes = set()


            for line in lines:
                net = line.amount.net
                vat = line.amount.tax
                gross = line.amount.gross
                not_evidenced = line.amount.non_tax_cost
                total_net += net
                total_vat += vat
                total_gross += gross
                total_not_evidenced += not_evidenced

                if line.contract_id is not None:
                    code = contracts.get(line.contract_id)
                    if code is not None:
                        contract_codes.add(code)

            result.append(
                InvoiceReviewItemView(
                    invoice_id=inv.id,
                    invoice_number=inv.invoice_number,
                    invoice_date=inv.invoice_date,
                    buyer_name=buyer.name if buyer else "UNKNOWN",
                    buyer_tax_number=buyer.tax_number if buyer else "UNKNOWN",
                    seller_name=seller.name if seller else "UNKNOWN",
                    seller_tax_number=seller.tax_number if seller else "UNKNOWN",
                    status=inv.status.value,
                    payment_method=inv.payment_method.value,
                    payment_status=inv.payment_status.value,
                    due_date=inv.due_date,
                    seller_bank_account=seller.bank_account.number if seller and seller.bank_account else None,
                    total_net=total_net,
                    total_vat=total_vat,
                    total_gross=total_gross,
                    total_not_evidenced=total_not_evidenced,
                    scan_filename = inv.scan_filename,
                    contract_codes=", ".join(contract_codes),
                    direction=direction.value if direction else None,
                )
            )

        return result
