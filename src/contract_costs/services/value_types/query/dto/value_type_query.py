from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ValueTypeQuery:
    organization_id: UUID
    code: str | None = None          # strict
    direction: str | None = None  # "COST" | "REVENUE"
    include_inactive: bool = False
    search: str | None = None        # name + description
