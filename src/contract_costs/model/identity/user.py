from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class User:
    id: UUID

    # identyfikacja
    login: str  # unikalny login (np. jarek, admin, księgowa)
    email: str | None  # opcjonalny
    full_name: str | None

    # status
    is_active: bool

    # audyt
    created_at: datetime
    created_by_user_id: UUID | None

    updated_at: datetime | None = None
    updated_by_user_id: UUID | None = None

    # przyszłość (auth, ale nie teraz)
    password_hash: str | None = None
    last_login_at: datetime | None = None
