from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.financial_records.queries.dto.financial_record_details_query import (
    FinancialRecordDetailsQuery,
)
from contract_costs.services.financial_records.queries.financial_record_details_query_service import (
    FinancialRecordDetailsQueryService,
)


def test_financial_record_details_query_service_builds_view(monkeypatch) -> None:
    org_id = uuid4()
    record_id = uuid4()
    buyer = CompanyBuilder().with_id(uuid4()).with_role(CompanyType.OWN).with_name("Buyer").build()
    seller = CompanyBuilder().with_id(uuid4()).with_role(CompanyType.SUPPLIER).with_name("Seller").build()

    record = (
        FinancialRecordBuilder()
        .with_id(record_id)
        .with_organization_id(org_id)
        .with_buyer_id(buyer.id)
        .with_seller_id(seller.id)
        .with_reference("FV/1")
        .with_invoice_date(date(2026, 2, 17))
        .build()
    )

    contract = ContractBuilder().with_id(uuid4()).with_code("C-1").build()
    node = SimpleNamespace(code="N-1")
    value_type = SimpleNamespace(code="VT-1")

    line = (
        FinancialRecordLineBuilder()
        .with_financial_record_id(record_id)
        .with_contract_id(contract.id)
        .with_contract_node_id(uuid4())
        .with_value_type_id(uuid4())
        .with_amount(Amount(
            value=Decimal("100"),
            input_type=AmountInputType.NET,
            vat_rate=VatRate.VAT_23,
            tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
        ))
        .build()
    )

    monkeypatch.setattr(
        "contract_costs.services.financial_records.queries.financial_record_details_query_service.RecordCompletionValidator.resolve_financial_record_direction",
        staticmethod(lambda *_args, **_kwargs: ValueDirection.COST),
    )

    uow = SimpleNamespace(
        financial_records=SimpleNamespace(get=lambda **_: record, get_by_reference=lambda **_: [record]),
        financial_record_lines=SimpleNamespace(list_by_financial_record=lambda **_: [line]),
        companies=SimpleNamespace(get=lambda **kwargs: buyer if kwargs["company_id"] == buyer.id else seller),
        contracts=SimpleNamespace(get=lambda **_: contract),
        contract_nodes=SimpleNamespace(get=lambda **_: node),
        value_types=SimpleNamespace(get=lambda **_: value_type),
    )
    query = FinancialRecordDetailsQuery(organization_id=org_id, actor_user_id=uuid4(), record_id=record_id)

    result = FinancialRecordDetailsQueryService().execute(action=query, uow=uow)

    assert result.reference == "FV/1"
    assert result.total_net == Decimal("100")
    assert result.total_vat == Decimal("23.00")
    assert result.contract_codes == "C-1"
    assert result.direction == "COST"


def test_financial_record_details_query_service_resolve_record_requires_id_or_ref() -> None:
    service = FinancialRecordDetailsQueryService()
    query = FinancialRecordDetailsQuery(organization_id=uuid4(), actor_user_id=uuid4())

    with pytest.raises(RuntimeError, match="Either record_id or reference"):
        service._resolve_record(action=query, record_repo=SimpleNamespace())



def test_company_view_marks_company_to_verify() -> None:
    from contract_costs.model.company import CompanyVerificationStatus

    to_verify = CompanyBuilder().with_verification_status(CompanyVerificationStatus.TO_VERIFY).build()
    verified = CompanyBuilder().build()

    assert FinancialRecordDetailsQueryService._map_company(to_verify).to_verify is True
    assert FinancialRecordDetailsQueryService._map_company(verified).to_verify is False
