import pytest

from contract_costs.common.ids import new_uuid
from contract_costs.model.number_sequence import NumberSequence

def test_create_initial_sets_value_to_one():
    seq = NumberSequence.create_initial(
        organization_id=new_uuid(),
        scope_key="invoice",
    )

    assert seq.current_value == 1

def test_increase_returns_incremented_value():
    seq = NumberSequence.create_initial(
        organization_id=new_uuid(),
        scope_key="invoice",
    )

    new_value = seq.increase()

    assert new_value == 2
    assert seq.current_value == 2

def test_multiple_increases():
    seq = NumberSequence.create_initial(
        organization_id=new_uuid(),
        scope_key="invoice",
    )

    seq.increase()
    seq.increase()

    assert seq.current_value == 3


def test_number_sequence_disallows_dynamic_attributes():
    seq = NumberSequence.create_initial(
        organization_id=new_uuid(),
        scope_key="invoice",
    )

    with pytest.raises(AttributeError):
        seq.random = 123


def test_increase_is_stateful():
    seq = NumberSequence.create_initial(
        organization_id=new_uuid(),
        scope_key="invoice",
    )

    first = seq.increase()
    second = seq.increase()

    assert first == 2
    assert second == 3
