from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveOrganizationUserCommand:
    organization_id: UUID
    target_user_id: UUID
    actor_user_id: UUID
