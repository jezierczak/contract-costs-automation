from dataclasses import dataclass
from uuid import UUID

@dataclass
class RequestContext:
    user:object | None = None
    organization:object | None = None
    membership:object | None = None

    user_id: UUID | None = None
    organization_id: UUID | None = None

    workspace_actions: str | None = None
    workspace_title: str | None = None
    workspace_subtitle: str | None = None
