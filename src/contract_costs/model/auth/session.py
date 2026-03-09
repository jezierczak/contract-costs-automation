from datetime import datetime
from dataclasses import dataclass,replace
from uuid import UUID


@dataclass(frozen=True,slots=True)
class Session:
    id: UUID
    user_id: UUID
    organization_id: UUID | None

    created_at: datetime
    expires_at: datetime

    def with_organization(self, organization_id: UUID) -> "Session":
        return replace(self, organization_id=organization_id)
