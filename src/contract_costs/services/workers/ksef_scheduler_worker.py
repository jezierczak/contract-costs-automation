import logging
import threading
from datetime import datetime, time, timedelta
from uuid import UUID

from contract_costs.common.time import local_now
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.services.ksef.dto.enqueue_ksef_auto_import_command import (
    EnqueueKsefAutoImportCommand,
)

logger = logging.getLogger(__name__)


class KsefSchedulerWorker:
    """
    Automatyczny import KSeF dla wszystkich organizacji:
    - po starcie aplikacji (z opóźnieniem) nadrabia firmy, które dziś nie
      miały jeszcze udanego importu,
    - codziennie o zadanych godzinach (czas polski) pobiera wszystkie firmy.

    Sam tylko zleca import do kolejki – pobieraniem zajmuje się KsefImportWorker.
    """

    def __init__(
        self,
        *,
        schedule_times: list[time],
        startup_delay_seconds: int,
    ) -> None:
        if not schedule_times:
            raise ValueError("KSeF scheduler requires at least one schedule time")
        self._schedule_times = sorted(schedule_times)
        self._startup_delay_seconds = startup_delay_seconds
        self._stop_event = threading.Event()

    @staticmethod
    def parse_schedule_times(raw: str) -> list[time]:
        return [time.fromisoformat(part.strip()) for part in raw.split(",") if part.strip()]

    def run(self) -> None:
        logger.info(
            "KSeF scheduler started (times=%s, startup_delay=%ss)",
            ", ".join(t.strftime("%H:%M") for t in self._schedule_times),
            self._startup_delay_seconds,
        )

        if self._stop_event.wait(self._startup_delay_seconds):
            return
        self._run_for_all_organizations(skip_imported_today=True)

        while not self._stop_event.is_set():
            now = local_now()
            next_run = self.next_run_at(now=now, schedule_times=self._schedule_times)
            logger.info("Next scheduled KSeF import at %s", next_run.isoformat())

            # timestamp() zamiast odejmowania – poprawnie przy zmianie czasu letni/zimowy
            if self._stop_event.wait(max(0.0, next_run.timestamp() - now.timestamp())):
                return
            self._run_for_all_organizations(skip_imported_today=False)

    def stop(self) -> None:
        logger.info("Stopping KSeF scheduler")
        self._stop_event.set()

    @staticmethod
    def next_run_at(*, now: datetime, schedule_times: list[time]) -> datetime:
        for scheduled in sorted(schedule_times):
            candidate = now.replace(
                hour=scheduled.hour,
                minute=scheduled.minute,
                second=0,
                microsecond=0,
            )
            if candidate > now:
                return candidate

        first = min(schedule_times)
        return (now + timedelta(days=1)).replace(
            hour=first.hour,
            minute=first.minute,
            second=0,
            microsecond=0,
        )

    @staticmethod
    def resolve_actor(memberships: list[OrganizationUser]) -> UUID | None:
        # Import zlecamy w imieniu najstarszego aktywnego OWNER-a organizacji
        # (przejdzie przez uprawnienia i będzie widoczny w logach zdarzeń).
        owners = [
            m for m in memberships
            if m.is_active and m.role == OrganizationRole.OWNER
        ]
        if not owners:
            return None
        return min(owners, key=lambda m: m.created_at).user_id

    def _run_for_all_organizations(self, *, skip_imported_today: bool) -> None:
        from contract_costs.cli.context import get_services

        services = get_services()

        try:
            with services.uow as uow:
                targets = []
                for organization in uow.organizations.list(active_only=True):
                    actor_user_id = self.resolve_actor(
                        uow.organization_users.list_by_organization(
                            organization.id,
                            active_only=True,
                        )
                    )
                    if actor_user_id is None:
                        logger.warning(
                            "Skipping scheduled KSeF import. No active OWNER in org=%s",
                            organization.id,
                        )
                        continue
                    targets.append((organization.id, actor_user_id))
        except Exception:
            logger.exception("Scheduled KSeF import failed while listing organizations")
            return

        for organization_id, actor_user_id in targets:
            try:
                result = services.action_bus.execute(
                    action=EnqueueKsefAutoImportCommand(
                        organization_id=organization_id,
                        actor_user_id=actor_user_id,
                        skip_imported_today=skip_imported_today,
                    ),
                    handler=services.enqueue_ksef_auto_import_service,
                )
                logger.info(
                    "Scheduled KSeF import (org=%s startup_catch_up=%s enqueued=%s "
                    "already_today=%s missing_first_import=%s)",
                    organization_id,
                    skip_imported_today,
                    [c.name for c in result.enqueued],
                    [c.name for c in result.already_imported_today],
                    [c.name for c in result.missing_first_import],
                )
            except Exception:
                logger.exception(
                    "Scheduled KSeF import failed (org=%s)",
                    organization_id,
                )
