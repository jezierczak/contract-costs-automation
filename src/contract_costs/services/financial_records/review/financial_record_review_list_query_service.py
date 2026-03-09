from decimal import Decimal
from typing import Any
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.company import Company
from contract_costs.model.contract import ContractType
from contract_costs.services.documents.document_selector import DocumentSelector

from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_validator import \
    RecordCompletionValidator


from contract_costs.services.financial_records.review.dto.invoice_review_item_view import FinancialRecordReviewItemView
from contract_costs.services.financial_records.review.dto.financial_record_review_query import FinancialRecordReviewQuery
from contract_costs.unit_of_work import UnitOfWork


class FinancialRecordReviewListQueryService(
    ActionHandler[FinancialRecordReviewQuery, list[FinancialRecordReviewItemView]]
):

    def execute(
        self,
        *,
        action: FinancialRecordReviewQuery,
        uow: UnitOfWork,
    ) -> list[FinancialRecordReviewItemView]:

        record_repo = uow.financial_records
        company_repo = uow.companies
        record_line_repo = uow.financial_record_lines
        contract_repo = uow.contracts

        records = record_repo.list_for_review(
            organization_id=action.organization_id,
            query=action,
        )

        if not records:
            return []

        record_ids = [r.id for r in records]

        # ----------------------------
        # preload companies
        # ----------------------------

        company_ids = {
            r.buyer_id for r in records
        } | {
            r.seller_id for r in records
        }
        companies_map: dict[UUID, Company] = {}

        for company_id in company_ids:
            company = company_repo.get(
                organization_id=action.organization_id,
                company_id=company_id,
            )
            if company:
                companies_map[company_id] = company

        # ----------------------------
        # preload lines
        # ----------------------------

        lines = record_line_repo.list_by_financial_record_ids(
            organization_id=action.organization_id,
            financial_records_ids=record_ids,
        )

        lines_map: dict[UUID, list] = {}

        for line in lines:
            lines_map.setdefault(line.financial_record_id, []).append(line)

        # ----------------------------
        # contracts map
        # ----------------------------

        contracts: dict[UUID, str] = {
            c.id: c.code
            for c in contract_repo.list_all_by_type(
                organization_id=action.organization_id,
                contract_type=ContractType.PROJECT,
            )
        }

        filter_contract_codes = (
            set(action.contract_codes)
            if action.contract_codes
            else None
        )

        result: list[FinancialRecordReviewItemView] = []

        for rec in records:

            buyer = companies_map.get(rec.buyer_id)
            seller = companies_map.get(rec.seller_id)

            if buyer and seller:
                direction = RecordCompletionValidator.resolve_financial_record_direction(
                    buyer.role,
                    seller.role,
                )
            else:
                direction = None

            record_lines = lines_map.get(rec.id, [])

            total_net = Decimal("0")
            total_vat = Decimal("0")
            total_gross = Decimal("0")
            total_not_evidenced = Decimal("0")

            contract_codes = set()

            for line in record_lines:

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

                if line.contract_id:

                    code = contracts.get(line.contract_id)

                    if code:
                        contract_codes.add(code)

            result.append(
                FinancialRecordReviewItemView(
                    record_id=rec.id,
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
                    seller_bank_account=(
                        seller.bank_account.account_number
                        if seller and seller.bank_account
                        else None
                    ),
                    total_net=total_net,
                    total_vat=total_vat,
                    total_gross=total_gross,
                    total_not_evidenced=total_not_evidenced,
                    primary_document_path=DocumentSelector().resolve_primary_path(
                        documents=rec.documents
                    ),
                    contract_codes=", ".join(contract_codes),
                    direction=direction.value if direction else None,
                )
            )

        return result

