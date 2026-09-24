from datetime import date, datetime, timezone
from queue import Queue
from uuid import uuid4

from contract_costs.model.company import CompanyType
from contract_costs.model.company_ksef_settings import CompanyKsefSettings, KsefEnvironment
from contract_costs.services.ksef.dto.enqueue_ksef_auto_import_command import (
    EnqueueKsefAutoImportCommand,
)
from contract_costs.services.ksef.enqueue_ksef_auto_import_service import (
    EnqueueKsefAutoImportService,
)
from contract_costs.services.workers.dto.ksef_import_queue_item import KsefImportDateType
from tests.builders.company_builder import CompanyBuilder

TODAY = date(2026, 9, 24)


def _add_company(uow, organization_id, *, name, role=CompanyType.OWN, is_active=True):
    company = (
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_name(name)
        .with_role(role)
        .with_is_active(is_active)
        .build()
    )
    uow.companies.add(company)
    return company


def _add_settings(uow, organization_id, company, *, is_enabled=True, last_import_from=None):
    uow.company_ksef_settings.add(
        organization_id=organization_id,
        settings=CompanyKsefSettings(
            id=uuid4(),
            organization_id=organization_id,
            company_id=company.id,
            environment=KsefEnvironment.TEST,
            is_enabled=is_enabled,
            certificate_path=None,
            certificate_password=None,
            last_import_from=last_import_from,
            last_import_at=None,
            last_error=None,
            created_at=datetime.now(timezone.utc),
            created_by_user_id=None,
            updated_at=None,
            updated_by_user_id=None,
        ),
    )


def _run(uow, organization_id, actor_user_id):
    queue = Queue()
    service = EnqueueKsefAutoImportService(queue=queue, today=lambda: TODAY)
    result = service.execute(
        action=EnqueueKsefAutoImportCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        ),
        uow=uow,
    )
    items = []
    while not queue.empty():
        items.append(queue.get_nowait())
    return result, items


def test_enqueues_every_enabled_own_company_from_last_import(uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    first = _add_company(uow, organization_id, name="Firma A")
    second = _add_company(uow, organization_id, name="Firma B")
    _add_settings(uow, organization_id, first, last_import_from=date(2026, 9, 20))
    _add_settings(uow, organization_id, second, last_import_from=date(2026, 9, 1))

    result, items = _run(uow, organization_id, actor_user_id)

    assert {c.id for c in result.enqueued} == {first.id, second.id}
    assert result.missing_first_import == []
    by_company = {item.company_id: item for item in items}
    assert by_company[first.id].from_date == date(2026, 9, 20)
    assert by_company[second.id].from_date == date(2026, 9, 1)
    for item in items:
        assert item.to_date == TODAY
        assert item.date_type == KsefImportDateType.PERMANENT_STORAGE
        assert item.organization_id == organization_id
        assert item.actor_user_id == actor_user_id


def test_company_without_first_import_is_skipped_and_reported(uow):
    organization_id = uuid4()
    company = _add_company(uow, organization_id, name="Nowa firma")
    _add_settings(uow, organization_id, company, last_import_from=None)

    result, items = _run(uow, organization_id, uuid4())

    assert items == []
    assert result.enqueued == []
    assert [c.id for c in result.missing_first_import] == [company.id]


def test_ignores_disabled_missing_settings_inactive_and_non_own_companies(uow):
    organization_id = uuid4()
    disabled = _add_company(uow, organization_id, name="Wyłączony KSeF")
    _add_settings(uow, organization_id, disabled, is_enabled=False, last_import_from=date(2026, 9, 1))
    _add_company(uow, organization_id, name="Bez konfiguracji")
    inactive = _add_company(uow, organization_id, name="Nieaktywna", is_active=False)
    _add_settings(uow, organization_id, inactive, last_import_from=date(2026, 9, 1))
    counterparty = _add_company(uow, organization_id, name="Kontrahent", role=CompanyType.SUPPLIER)
    _add_settings(uow, organization_id, counterparty, last_import_from=date(2026, 9, 1))

    result, items = _run(uow, organization_id, uuid4())

    assert items == []
    assert result.enqueued == []
    assert result.missing_first_import == []


def test_last_import_in_future_does_not_produce_inverted_range(uow):
    organization_id = uuid4()
    company = _add_company(uow, organization_id, name="Firma A")
    _add_settings(uow, organization_id, company, last_import_from=date(2026, 10, 5))

    _, items = _run(uow, organization_id, uuid4())

    assert items[0].from_date == TODAY
    assert items[0].to_date == TODAY


def _run_catch_up(uow, organization_id):
    queue = Queue()
    service = EnqueueKsefAutoImportService(queue=queue, today=lambda: TODAY)
    result = service.execute(
        action=EnqueueKsefAutoImportCommand(
            organization_id=organization_id,
            actor_user_id=uuid4(),
            skip_imported_today=True,
        ),
        uow=uow,
    )
    items = []
    while not queue.empty():
        items.append(queue.get_nowait())
    return result, items


def test_catch_up_skips_companies_already_imported_today(uow):
    organization_id = uuid4()
    done_today = _add_company(uow, organization_id, name="Pobrana dziś")
    _add_settings(uow, organization_id, done_today, last_import_from=TODAY)
    pending = _add_company(uow, organization_id, name="Pobrana wczoraj")
    _add_settings(uow, organization_id, pending, last_import_from=date(2026, 9, 23))

    result, items = _run_catch_up(uow, organization_id)

    assert [item.company_id for item in items] == [pending.id]
    assert [c.id for c in result.already_imported_today] == [done_today.id]


def test_regular_run_does_not_skip_companies_imported_today(uow):
    organization_id = uuid4()
    company = _add_company(uow, organization_id, name="Pobrana dziś")
    _add_settings(uow, organization_id, company, last_import_from=TODAY)

    result, items = _run(uow, organization_id, uuid4())

    assert [item.company_id for item in items] == [company.id]
    assert result.already_imported_today == []
