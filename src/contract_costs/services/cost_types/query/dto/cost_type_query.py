from dataclasses import dataclass


@dataclass(frozen=True)
class CostTypeQuery:
    code: str | None = None          # strict
    include_inactive: bool = False
    search: str | None = None        # name + description
