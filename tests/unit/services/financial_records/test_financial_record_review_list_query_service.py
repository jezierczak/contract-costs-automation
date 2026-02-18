from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from contract_costs.model.amount import Amount, TaxTreatment, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractType
from contract_costs.model.document import DocumentType
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.financial_records.review.dto.financial_record_review_query import (
    FinancialRecordReviewQuery,
)
from contract_costs.services.financial_records.review.financial_record_review_list_query_service import (
    FinancialRecordReviewListQueryService,
)


def test_financial_record_review_list_query_service_filters_by_contract_code(monkeypatch) -> None:
    org_id = uuid4()
    buyer = CompanyBuilder().with_id(uuid4()).with_role(CompanyType.OWN).with_name("Buyer").build()
    seller = CompanyBuilder().with_id(uuid4()).with_role(CompanyType.SUPPLIER).with_name("Seller").with_bank_account("123", "PL").build()
    contract = ContractBuilder().with_id(uuid4()).with_code("C-1").with_contract_type(ContractType.PROJECT).build()
    doc = DocumentBuilder().with_file_path("p/a.pdf").with_document_type(DocumentType.INVOICE).build()

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_buyer_id(buyer.id)
        .with_seller_id(seller.id)
        .with_reference("FV/1")
        .with_invoice_date(date(2026, 2, 17))
        .with_documents([doc])
        .build()
    )
    line = (
        FinancialRecordLineBuilder()
        .with_financial_record_id(record.id)
        .with_contract_id(contract.id)
        .with_amount(Amount(Decimal("100"), VatRate.VAT_23, TaxTreatment.TAX_DEDUCTIBLE))
        .build()
    )

    monkeypatch.setattr(
        "contract_costs.services.financial_records.review.financial_record_review_list_query_service.RecordCompletionValidator.resolve_financial_record_direction",
        staticmethod(lambda *_args, **_kwargs: ValueDirection.COST),
    )

    uow = SimpleNamespace(
        financial_records=SimpleNamespace(list_for_review=lambda **_: [record]),
        companies=SimpleNamespace(get=lambda **kwargs: buyer if kwargs["company_id"] == buyer.id else seller),
        financial_record_lines=SimpleNamespace(list_by_financial_record=lambda **_: [line]),
        contracts=SimpleNamespace(list_contracts=lambda **_: [contract]),
    )
    query = FinancialRecordReviewQuery(
        organization_id=org_id,
        actor_user_id=uuid4(),
        contract_codes=["C-1"],
    )

    result = FinancialRecordReviewListQueryService().execute(action=query, uow=uow)

    assert len(result) == 1
    assert result[0].total_net == Decimal("100")
    assert result[0].contract_codes == "C-1"
    assert result[0].primary_document_path == "p/a.pdf"
    assert result[0].direction == "COST"

