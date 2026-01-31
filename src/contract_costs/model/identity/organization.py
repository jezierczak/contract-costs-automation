from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class Organization:
    id: UUID

    # identyfikacja
    code: str                 # np. "REMONTIVO"
    name: str                 # pełna nazwa

    # status
    is_active: bool

    # audyt
    created_at: datetime
    created_by_user_id: UUID | None

    updated_at: datetime | None
    updated_by_user_id: UUID | None

    # przyszłość (na razie puste)
    settings: dict[str, Any] | None = None
