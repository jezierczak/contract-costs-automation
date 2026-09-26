from uuid import uuid4

import pytest

from contract_costs.model.company import CompanyType
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_reason import (
    FinancialRecordCompletionReason,
)
from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_validator import (
    RecordCompletionValidator,
)
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_assignment_facts import (
    FinancialRecordAssignmentFacts,
)
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder


def test_status_returns_ok_for_complete_cost_record():
    value_type_id = uuid4()
    line = (
        FinancialRecordLineBuilder()
        .with_contract_id(uuid4())
        .with_contract_node_id(uuid4())
        .with_value_type_id(value_type_id)
        .build()
    )
    facts = FinancialRecordAssignmentFacts(
        record_id=uuid4(),
        invoice_lines=[line],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.SUPPLIER,
        value_type_directions_map={value_type_id: ValueDirection.COST},
    )

    validator = RecordCompletionValidator()
    reasons = validator.status(facts)

    assert reasons == [FinancialRecordCompletionReason.OK]
    assert validator.validate(facts) is True


def test_status_reports_incomplete_and_mismatch_issues():
    value_type_id = uuid4()
    incomplete_line = (
        FinancialRecordLineBuilder()
        .with_contract_id(None)
        .with_contract_node_id(None)
        .with_value_type_id(value_type_id)
        .build()
    )
    facts = FinancialRecordAssignmentFacts(
        record_id=uuid4(),
        invoice_lines=[incomplete_line],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.SUPPLIER,
        value_type_directions_map={value_type_id: ValueDirection.REVENUE},
    )

    reasons = RecordCompletionValidator().status(facts)

    assert FinancialRecordCompletionReason.INCOMPLETE_LINES in reasons
    assert FinancialRecordCompletionReason.DIRECTION_MISMATCH in reasons
    assert FinancialRecordCompletionReason.OK not in reasons


def test_status_raises_when_value_type_direction_missing():
    missing_type_id = uuid4()
    line = (
        FinancialRecordLineBuilder()
        .with_contract_id(uuid4())
        .with_contract_node_id(uuid4())
        .with_value_type_id(missing_type_id)
        .build()
    )
    facts = FinancialRecordAssignmentFacts(
        record_id=uuid4(),
        invoice_lines=[line],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.SUPPLIER,
        value_type_directions_map={},
    )

    with pytest.raises(RuntimeError, match="Missing value_type_direction"):
        RecordCompletionValidator().status(facts)


def test_status_blocks_record_with_company_to_verify():
    value_type_id = uuid4()
    line = (
        FinancialRecordLineBuilder()
        .with_contract_id(uuid4())
        .with_contract_node_id(uuid4())
        .with_value_type_id(value_type_id)
        .build()
    )
    facts = FinancialRecordAssignmentFacts(
        record_id=uuid4(),
        invoice_lines=[line],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.SUPPLIER,
        value_type_directions_map={value_type_id: ValueDirection.COST},
        companies_verified=False,
    )

    validator = RecordCompletionValidator()

    assert validator.status(facts) == [FinancialRecordCompletionReason.COMPANY_TO_VERIFY]
    assert validator.validate(facts) is False
