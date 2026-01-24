from dataclasses import dataclass


@dataclass(frozen=True)
class ValueTypeQuery:
    code: str | None = None          # strict
    direction: str | None = None  # "COST" | "REVENUE"
    include_inactive: bool = False
    search: str | None = None        # name + description
