from datetime import date
from typing import NamedTuple
from uuid import UUID


class KsefImportQueueItem(NamedTuple):
    organization_id: UUID
    actor_user_id: UUID
    company_id: UUID
    from_date: date
    to_date: date
