from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateUserCommand:
    login: str
    email: str | None
    full_name: str | None
    created_by_user_id: UUID | None

