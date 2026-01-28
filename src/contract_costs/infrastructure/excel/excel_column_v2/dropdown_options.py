from dataclasses import dataclass


@dataclass(frozen=True)
class DropdownOptions:
    """
    dictionaries:
        logical dictionary id -> list of values
        key MUST match value coming from depends_on column

    depends_on:
        name of column this dropdown depends on
        None => static dropdown
    """
    dictionary: str              # logical dictionary id
    value_column: str = "VALUE"  # column used for dropdown
    depends_on: str | None = None
