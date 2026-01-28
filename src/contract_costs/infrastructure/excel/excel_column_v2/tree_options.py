from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class TreeOptions[T]:
    """
    Generic tree description for Excel / CLI.
    """
    id: Callable[[T], object]
    parent_id: Callable[[T], object | None]

    # order children (optional)
    sort_key: Callable[[T], str | int | float] | None = None

    # node state
    is_active: Callable[[T], bool] | None = None

