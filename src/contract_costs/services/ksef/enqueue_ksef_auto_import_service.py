from dataclasses import dataclass, field
from datetime import date
from queue import Queue
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import local_today
from contract_costs.model.company import Company
from contract_costs.services.ksef.dto.enqueue_ksef_auto_import_command import (
    EnqueueKsefAutoImportCommand,
)
from contract_costs.services.queue.ksef_import_queue import ksef_import_queue
from contract_costs.services.workers.dto.ksef_import_queue_item import (
    KsefImportDateType,
    KsefImportQueueItem,
)
from contract_costs.unit_of_work import UnitOfWork


@dataclass(frozen=True, slots=True)
class KsefAutoImportResult:
    enqueued: list[Company] = field(default_factory=list)
    # KSeF włączony, ale nigdy nie było importu – nie wiemy, od kiedy pobierać,
    # więc użytkownik musi najpierw zrobić jednorazowy import ręczny.
    missing_first_import: list[Company] = field(default_factory=list)
    already_imported_today: list[Company] = field(default_factory=list)


class EnqueueKsefAutoImportService(ActionHandler[EnqueueKsefAutoImportCommand, KsefAutoImportResult]):
    """
    Zleca import KSeF dla wszystkich aktywnych firm własnych z włączonym KSeF,
    od ostatniego pobrania (last_import_from) do dziś. Zapytanie idzie po dacie
    przyjęcia do KSeF, żeby nie gubić faktur wysłanych do KSeF z opóźnieniem.
    """

    def __init__(
        self,
        *,
        queue: Queue[KsefImportQueueItem] = ksef_import_queue,
        today: Callable[[], date] = local_today,
    ) -> None:
        self._queue = queue
        self._today = today

    def execute(
        self,
        *,
        action: EnqueueKsefAutoImportCommand,
        uow: UnitOfWork,
    ) -> KsefAutoImportResult:
        today = self._today()
        result = KsefAutoImportResult()

        for company in uow.companies.get_owners(action.organization_id):
            if not company.is_active:
                continue

            settings = uow.company_ksef_settings.get_by_company_id(
                organization_id=action.organization_id,
                company_id=company.id,
            )
            if settings is None or not settings.is_enabled:
                continue

            if settings.last_import_from is None:
                result.missing_first_import.append(company)
                continue

            # last_import_from ustawia się na datę "do" dopiero po udanym
            # imporcie, więc import zakończony dziś błędem nie jest pomijany.
            if action.skip_imported_today and settings.last_import_from >= today:
                result.already_imported_today.append(company)
                continue

            # Zaczynamy od dnia ostatniego pobrania (a nie dnia następnego), bo
            # tamten import mógł nie złapać faktur przyjętych później tego dnia.
            # Duplikaty odrzuca upload (DuplicateDocument).
            self._queue.put(
                KsefImportQueueItem(
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                    company_id=company.id,
                    from_date=min(settings.last_import_from, today),
                    to_date=today,
                    date_type=KsefImportDateType.PERMANENT_STORAGE,
                )
            )
            result.enqueued.append(company)

        return result
