from uuid import UUID


def resolve_or_none(getter, code: str | None, label: str) -> UUID | None:
    """
    getter: repo.get_by_code
    code: np. 'TAUR'
    label: nazwa encji do komunikatu błędu
    """
    if not code:
        return None

    entity = getter(code)
    if entity is None:
        raise ValueError(f"{label} not found for code: {code}")

    return entity.id
