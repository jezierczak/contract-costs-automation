from typing import NamedTuple
from uuid import UUID


class DocumentProcessQueueItem(NamedTuple):
    organization_id: UUID
    actor_user_id: UUID
    document_id: UUID