from datetime import datetime
from uuid import uuid4

from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.repository.inmemory.financial_record_repository import (
    InMemoryFinancialRecordRepository,
)
from contract_costs.services.financial_records.assigment.ingest.financial_record_ingest_service import (
    FinancialRecordIngestService,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder


class _DummyIngestService(FinancialRecordIngestService):
    def apply(self, *, uow, organization_id, actor_user_id, updates):
        return {}


def test_get_existing_record_prefers_explicit_record_id():
    organization_id = uuid4()
    seller = CompanyBuilder().build()
    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_seller_id(seller.id)
        .with_reference("FV/100")
        .build()
    )
    repo = InMemoryFinancialRecordRepository()
    repo.add(record)

    service = _DummyIngestService()
    update = type("U", (), {"record_id": record.id, "reference": "OTHER", "seller": seller})()

    existing = service._get_existing_record(
        record_repo=repo,
        organization_id=organization_id,
        update=update,
    )

    assert existing is not None
    assert existing.id == record.id


def test_mark_processed_sets_status_to_processed():
    organization_id = uuid4()
    actor_user_id = uuid4()
    now = datetime(2026, 2, 12, 22, 15, 0)
    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_status(FinancialRecordStatus.IN_PROGRESS)
        .build()
    )
    repo = InMemoryFinancialRecordRepository()
    repo.add(record)

    service = _DummyIngestService(clock=lambda: now)
    service.mark_processed(
        record_repo=repo,
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        record_ids=[record.id],
    )

    updated = repo.get(organization_id=organization_id, record_id=record.id)
    assert updated is not None
    assert updated.status == FinancialRecordStatus.PROCESSED
    assert updated.updated_at == now
    assert updated.updated_by_user_id == actor_user_id


def test_resolve_tags_splits_and_trims():
    tags = _DummyIngestService._resolve_tags("a, b , ,c")
    assert tags == {"a", "b", "c"}
