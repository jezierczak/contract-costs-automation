from decimal import Decimal
from uuid import uuid4

from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.inmemory.financial_record_line_repository import (
    InMemoryFinancialRecordLineRepository,
)
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_ref_result import (
    FinancialRecordRefResult,
    RecordApplyAction,
)
from contract_costs.services.financial_records.assigment.ingest.financial_record_line_update_service import (
    FinancialRecordLineUpdateService,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    FinancialRecordLineUpdate,
)


class _FakeUow:
    def __init__(self, *, line_repo, contract_repo, node_repo, value_type_repo):
        self.financial_record_lines = line_repo
        self.contracts = contract_repo
        self.contract_nodes = node_repo
        self.value_types = value_type_repo


def _line_update(*, record_reference: str | None, record_line_id=None) -> FinancialRecordLineUpdate:
    return FinancialRecordLineUpdate(
        record_line_id=record_line_id,
        record_reference=record_reference,
        item_name="item",
        description="desc",
        quantity=Decimal("1"),
        unit=UnitOfMeasure.PIECE,
        amount=Amount(Decimal("100"), VatRate.VAT_23),
        contract_reference="C-1",
        contract_node_reference="N-1",
        value_type_reference="VT-1",
        agreement_reference=None,
        agreement_node_reference=None
    )


def test_resolve_ref_matches_old_reference():
    ref_result = FinancialRecordRefResult(
        record_id=uuid4(),
        action=RecordApplyAction.APPLIED,
        record_reference="NEW/1",
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.SUPPLIER,
        old_record_reference="OLD/1",
    )
    resolved = FinancialRecordLineUpdateService._resolve_ref(
        _line_update(record_reference="OLD/1"),
        {"NEW/1": ref_result},
    )
    assert resolved == ref_result


def test_apply_creates_line_and_returns_assignment_facts():
    organization_id = uuid4()
    actor_user_id = uuid4()
    record_id = uuid4()
    value_type_id = uuid4()
    contract_id = uuid4()
    node_id = uuid4()

    line_repo = InMemoryFinancialRecordLineRepository()
    contract_repo = type("R", (), {"get_by_code": lambda self, org, code: type("E", (), {"id": contract_id})()})()
    node_repo = type("R", (), {"get_by_code": lambda self, org, code: type("E", (), {"id": node_id})()})()
    value_type_repo = type(
        "R",
        (),
        {
            "get_by_code": lambda self, org, code: type("E", (), {"id": value_type_id})(),
            "list_all": lambda self, organization_id: [
                type("VT", (), {"id": value_type_id, "direction": ValueDirection.COST})()
            ],
        },
    )()

    service = FinancialRecordLineUpdateService()
    uow = _FakeUow(
        line_repo=line_repo,
        contract_repo=contract_repo,
        node_repo=node_repo,
        value_type_repo=value_type_repo,
    )

    ref_map = {
        "FV/1": FinancialRecordRefResult(
            record_id=record_id,
            action=RecordApplyAction.APPLIED,
            record_reference="FV/1",
            buyer_role=CompanyType.OWN,
            seller_role=CompanyType.SUPPLIER,
        )
    }

    facts_map = service.apply(
        uow=uow,
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        lines=[_line_update(record_reference="FV/1")],
        ref_map=ref_map,
    )

    saved_lines = line_repo.list_by_financial_record(
        organization_id=organization_id,
        financial_record_id=record_id,
    )
    assert len(saved_lines) == 1
    assert saved_lines[0].contract_id == contract_id
    assert saved_lines[0].value_type_id == value_type_id

    assert record_id in facts_map
    facts = facts_map[record_id]
    assert len(facts.invoice_lines) == 1
    assert facts.buyer_role == CompanyType.OWN
    assert facts.value_type_directions_map[value_type_id] == ValueDirection.COST


def test_apply_skips_line_when_reference_not_found_in_batch():
    organization_id = uuid4()
    line_repo = InMemoryFinancialRecordLineRepository()
    empty_repo = type(
        "R",
        (),
        {
            "get_by_code": lambda self, org, code: None,
            "list_all": lambda self, organization_id: [],
        },
    )()

    service = FinancialRecordLineUpdateService()
    uow = _FakeUow(
        line_repo=line_repo,
        contract_repo=empty_repo,
        node_repo=empty_repo,
        value_type_repo=empty_repo,
    )

    facts_map = service.apply(
        uow=uow,
        organization_id=organization_id,
        actor_user_id=uuid4(),
        lines=[_line_update(record_reference="MISSING")],
        ref_map={},
    )

    assert facts_map == {}
    assert line_repo.list_all(organization_id=organization_id) == []
