from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateOrganizationCommand:
    organization_code: str
    organization_name: str

    owner_login: str
    owner_email: str | None
    owner_full_name: str | None

    created_by_user_id: UUID | None  # None przy self-signup
