from datetime import date
from enum import Enum
from typing import NamedTuple
from uuid import UUID


class KsefImportDateType(Enum):
    # data wystawienia faktury – naturalna przy ręcznym imporcie "faktury z września"
    ISSUE = "issue"
    # data przyjęcia faktury do KSeF – przy imporcie przyrostowym nie gubi faktur
    # wystawionych wcześniej, a wysłanych do KSeF z opóźnieniem (np. tryb offline)
    PERMANENT_STORAGE = "permanent_storage"


class KsefImportQueueItem(NamedTuple):
    organization_id: UUID
    actor_user_id: UUID
    company_id: UUID
    from_date: date
    to_date: date
    date_type: KsefImportDateType = KsefImportDateType.ISSUE
