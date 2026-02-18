from uuid import uuid4

import pytest

from contract_costs.repository.inmemory.financial_record_repository import InMemoryFinancialRecordRepository
from contract_costs.services.financial_records.actions.dto.invoice_action_command import (
    FinancialRecordSelector,
)
from contract_costs.services.financial_records.actions.financial_record_selector_resolver import (
    FinancialRecordSelectorResolver,
)
from tests.builders.financial_record_builder import FinancialRecordBuilder


def test_resolve_by_record_id():
    organization_id = uuid4()
    record = FinancialRecordBuilder().with_organization_id(organization_id).build()
    repo = InMemoryFinancialRecordRepository()
    repo.add(record)

    resolver = FinancialRecordSelectorResolver(repo)
    resolved = resolver.resolve(
        organization_id=organization_id,
        selectors=[FinancialRecordSelector(record_id=record.id)],
    )

    assert resolved == [record.id]


def test_resolve_by_reference_raises_on_ambiguous_match():
    organization_id = uuid4()
    reference = "FV/1/2026"

    first = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_reference(reference)
        .with_seller_id(uuid4())
        .build()
    )
    second = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_reference(reference)
        .with_seller_id(uuid4())
        .build()
    )

    repo = InMemoryFinancialRecordRepository()
    repo.add(first)
    repo.add(second)

    resolver = FinancialRecordSelectorResolver(repo)

    with pytest.raises(RuntimeError, match="Ambiguous financial record reference"):
        resolver.resolve(
            organization_id=organization_id,
            selectors=[FinancialRecordSelector(record_reference=reference)],
        )


def test_resolve_by_reference_raises_when_not_found():
    resolver = FinancialRecordSelectorResolver(InMemoryFinancialRecordRepository())

    with pytest.raises(ValueError, match="FinancialRecord not found"):
        resolver.resolve(
            organization_id=uuid4(),
            selectors=[FinancialRecordSelector(record_reference="MISSING")],
        )
