from datetime import datetime, time, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

import contract_costs.cli.context as context_module
from contract_costs.common.time import APP_TIMEZONE
from contract_costs.services.ksef.enqueue_ksef_auto_import_service import KsefAutoImportResult
from contract_costs.services.workers.ksef_scheduler_worker import KsefSchedulerWorker
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.organization_user_builder import OrganizationUserBuilder

TIMES = [time(8, 0), time(18, 0)]


def _at(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 9, day, hour, minute, tzinfo=APP_TIMEZONE)


@pytest.mark.parametrize(
    ("now", "expected"),
    [
        (_at(24, 6, 30), _at(24, 8)),
        (_at(24, 8, 0), _at(24, 18)),  # dokładnie o 8:00 – już uruchomione, następne o 18
        (_at(24, 12), _at(24, 18)),
        (_at(24, 18, 1), _at(25, 8)),
        (_at(24, 23, 59), _at(25, 8)),
    ],
)
def test_next_run_at(now, expected):
    assert KsefSchedulerWorker.next_run_at(now=now, schedule_times=TIMES) == expected


def test_parse_schedule_times():
    assert KsefSchedulerWorker.parse_schedule_times(" 18:00, 08:00 ,") == [time(18, 0), time(8, 0)]


def test_resolve_actor_picks_oldest_active_owner():
    org_id = uuid4()
    base = datetime(2026, 1, 1)
    older_owner = (
        OrganizationUserBuilder().with_organization_id(org_id).as_owner()
        .with_created(base, None).build()
    )
    newer_owner = (
        OrganizationUserBuilder().with_organization_id(org_id).as_owner()
        .with_created(base + timedelta(days=1), None).build()
    )
    inactive_owner = (
        OrganizationUserBuilder().with_organization_id(org_id).as_owner()
        .with_created(base - timedelta(days=1), None).inactive().build()
    )
    admin = (
        OrganizationUserBuilder().with_organization_id(org_id).as_admin()
        .with_created(base - timedelta(days=2), None).build()
    )

    actor = KsefSchedulerWorker.resolve_actor([newer_owner, admin, inactive_owner, older_owner])

    assert actor == older_owner.user_id


def test_resolve_actor_returns_none_without_owner():
    admin = OrganizationUserBuilder().as_admin().build()

    assert KsefSchedulerWorker.resolve_actor([admin]) is None


def test_run_enqueues_every_active_organization_as_its_owner(monkeypatch):
    uow = InMemoryUnitOfWork()
    org_a = OrganizationBuilder().build()
    org_b = OrganizationBuilder().build()
    org_inactive = OrganizationBuilder().inactive().build()
    org_without_owner = OrganizationBuilder().build()
    for org in (org_a, org_b, org_inactive, org_without_owner):
        uow.organizations.add(org)
    owner_a = OrganizationUserBuilder().with_organization_id(org_a.id).as_owner().build()
    owner_b = OrganizationUserBuilder().with_organization_id(org_b.id).as_owner().build()
    owner_inactive_org = OrganizationUserBuilder().with_organization_id(org_inactive.id).as_owner().build()
    admin_only = OrganizationUserBuilder().with_organization_id(org_without_owner.id).as_admin().build()
    for membership in (owner_a, owner_b, owner_inactive_org, admin_only):
        uow.organization_users.add(membership)

    executed = []

    def execute(*, action, handler):
        executed.append(action)
        return KsefAutoImportResult()

    fake_services = SimpleNamespace(
        uow=uow,
        action_bus=SimpleNamespace(execute=execute),
        enqueue_ksef_auto_import_service=object(),
    )
    monkeypatch.setattr(context_module, "get_services", lambda: fake_services)

    worker = KsefSchedulerWorker(schedule_times=TIMES, startup_delay_seconds=0)
    worker._run_for_all_organizations(skip_imported_today=True)

    assert {(a.organization_id, a.actor_user_id) for a in executed} == {
        (org_a.id, owner_a.user_id),
        (org_b.id, owner_b.user_id),
    }
    assert all(a.skip_imported_today for a in executed)


def test_one_organization_failure_does_not_stop_others(monkeypatch):
    uow = InMemoryUnitOfWork()
    orgs = [OrganizationBuilder().build() for _ in range(2)]
    for org in orgs:
        uow.organizations.add(org)
        uow.organization_users.add(
            OrganizationUserBuilder().with_organization_id(org.id).as_owner().build()
        )

    executed = []

    def execute(*, action, handler):
        executed.append(action.organization_id)
        if len(executed) == 1:
            raise RuntimeError("boom")
        return KsefAutoImportResult()

    fake_services = SimpleNamespace(
        uow=uow,
        action_bus=SimpleNamespace(execute=execute),
        enqueue_ksef_auto_import_service=object(),
    )
    monkeypatch.setattr(context_module, "get_services", lambda: fake_services)

    KsefSchedulerWorker(schedule_times=TIMES, startup_delay_seconds=0)._run_for_all_organizations(
        skip_imported_today=False
    )

    assert len(executed) == 2


def test_stop_during_startup_delay_exits_without_import(monkeypatch):
    calls = []
    worker = KsefSchedulerWorker(schedule_times=TIMES, startup_delay_seconds=3600)
    monkeypatch.setattr(worker, "_run_for_all_organizations", lambda **kw: calls.append(kw))

    worker.stop()
    worker.run()

    assert calls == []
