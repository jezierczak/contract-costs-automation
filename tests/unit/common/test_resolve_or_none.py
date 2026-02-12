from uuid import uuid4
import pytest

from contract_costs.services.common.resolve_utils import resolve_or_none


class Dummy:
    def __init__(self, id):
        self.id = id


def test_resolve_or_none_returns_id_when_found():
    org_id = uuid4()
    entity_id = uuid4()

    def getter(org, code):
        return Dummy(entity_id)

    result = resolve_or_none(getter, org_id, "ABC", "Company")

    assert result == entity_id


def test_resolve_or_none_returns_none_when_code_missing():
    org_id = uuid4()

    def getter(org, code):
        return None

    assert resolve_or_none(getter, org_id, None, "Company") is None


def test_resolve_or_none_raises_when_not_found():
    org_id = uuid4()

    def getter(org, code):
        return None

    with pytest.raises(ValueError):
        resolve_or_none(getter, org_id, "X", "Company")
