from decimal import Decimal
from uuid import UUID

from contract_costs.model.contract import ContractType
from contract_costs.model.document import DocumentType, Document
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.services.documents.document_selector import DocumentSelector

from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_validator import \
    RecordCompletionValidator
from contract_costs.services.financial_records.review.dto.document_view import DocumentView

from contract_costs.services.financial_records.review.dto.invoice_review_item_view import FinancialRecordReviewItemView
from contract_costs.services.financial_records.review.dto.financial_record_review_query import FinancialRecordReviewQuery


class FinancialRecordReviewListQueryService:

    def __init__(
        self,
        record_repo: FinancialRecordRepository,
        company_repo: CompanyRepository,
        record_line_repo: FinancialRecordLineRepository,
        contract_repo: ContractRepository,
    ) -> None:
        self._record_repo = record_repo
        self._company_repo = company_repo
        self._record_line_repo = record_line_repo
        self._contract_repo = contract_repo

    def list_for_review(self,
                        *,
                        organization_id: UUID,
                        review_query: FinancialRecordReviewQuery) -> list[FinancialRecordReviewItemView]:

        records = self._record_repo.list_for_review(
            organization_id=organization_id,
            query=review_query)

        result = []

        contracts: dict[UUID, str] = {item.id:item.code for item in self._contract_repo.list_contracts(
            organization_id=organization_id,
            contract_type = ContractType.PROJECT,
        )}

        filter_contract_codes = (
            set(review_query.contract_codes)
            if review_query.contract_codes
            else None
        )

        for rec in records:
            buyer = self._company_repo.get(organization_id=organization_id,company_id=rec.buyer_id)
            seller = self._company_repo.get(organization_id=organization_id,company_id=rec.seller_id)

            if buyer and seller:
                direction= RecordCompletionValidator.resolve_financial_record_direction(buyer.role, seller.role)
            else: direction = None
            lines = self._record_line_repo.list_by_financial_record(
                organization_id=organization_id,
                financial_record_id=rec.id)
            total_net = Decimal("0")
            total_vat = Decimal("0")
            total_gross = Decimal("0")
            total_not_evidenced = Decimal("0")

            contract_codes = set()

            # documents = [
            #     DocumentView(
            #         filename=doc.filename,
            #         file_path=doc.file_path,
            #         document_type_=doc.document_type.value
            #     )
            #     for doc in rec.documents
            # ]


            for line in lines:
                # --- FILTER BY CONTRACT CODES (if provided) ---
                if filter_contract_codes is not None:
                    if line.contract_id is None:
                        continue

                    contract_code = contracts.get(line.contract_id)
                    if contract_code not in filter_contract_codes:
                        continue

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
                FinancialRecordReviewItemView(
                    invoice_id=rec.id,
                    reference=rec.reference,
                    invoice_date=rec.invoice_date,
                    buyer_name=buyer.name if buyer else "UNKNOWN",
                    buyer_tax_number=buyer.tax_number if buyer else "UNKNOWN",
                    seller_name=seller.name if seller else "UNKNOWN",
                    seller_tax_number=seller.tax_number if seller else "UNKNOWN",
                    status=rec.status.value,
                    payment_method=rec.payment_method.value,
                    payment_status=rec.payment_status.value,
                    due_date=rec.due_date,
                    seller_bank_account=seller.bank_account.account_number if seller and seller.bank_account else None,
                    total_net=total_net,
                    total_vat=total_vat,
                    total_gross=total_gross,
                    total_not_evidenced=total_not_evidenced,
                    primary_document_path = DocumentSelector().resolve_primary_path(documents=rec.documents),
                    contract_codes=", ".join(contract_codes),
                    direction=direction.value if direction else None,
                )
            )

        return result

