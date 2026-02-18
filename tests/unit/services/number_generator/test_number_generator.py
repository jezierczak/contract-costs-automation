from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from contract_costs.model.number_sequence import NumberSequence
from contract_costs.services.number_generator.number_generator import NumberGenerator


def test_generate_without_auto_skips_uow():
    uow = MagicMock()
    service = NumberGenerator()

    result = service.generate(
        uow=uow,
        organization_id=uuid4(),
        pattern="INV/<Y>/<m>",
        date=datetime(2026, 2, 12),
    )

    assert result == "INV/2026/02"
    uow.number_sequences.get_for_update.assert_not_called()


def test_generate_with_auto_creates_initial_sequence():
    uow = MagicMock()
    uow.number_sequences.get_for_update.return_value = None

    service = NumberGenerator()
    organization_id = uuid4()

    result = service.generate(
        uow=uow,
        organization_id=organization_id,
        pattern="INV/<Y>/<m>/<auto>",
        date=datetime(2026, 2, 12),
    )

    assert result == "INV/2026/02/1"

    uow.number_sequences.get_for_update.assert_called_once_with(
        organization_id,
        "INV/2026/02"
    )

    uow.number_sequences.add.assert_called_once()
    added_sequence = uow.number_sequences.add.call_args.args[0]

    assert isinstance(added_sequence, NumberSequence)
    assert added_sequence.current_value == 1

    uow.number_sequences.update.assert_not_called()

def test_generate_with_auto_increases_existing_sequence():
    organization_id = uuid4()

    sequence = NumberSequence(
        organization_id=organization_id,
        scope_key="INV/2026/02",
        current_value=1,
    )

    uow = MagicMock()
    uow.number_sequences.get_for_update.return_value = sequence

    service = NumberGenerator()

    result = service.generate(
        uow=uow,
        organization_id=organization_id,
        pattern="INV/<Y>/<m>/<auto>",
        date=datetime(2026, 2, 12),
    )

    assert result == "INV/2026/02/2"
    assert sequence.current_value == 2

    uow.number_sequences.update.assert_called_once_with(sequence)
    uow.number_sequences.add.assert_not_called()


def test_helpers_resolve_context_and_scope_key():
    resolved = NumberGenerator._resolve_context(
        pattern="INV-<Y>-<m>-<auto>",
        date=datetime(2026, 2, 12),
    )
    assert resolved == "INV-2026-02-<auto>"

    scope = NumberGenerator._build_scope_key("INV-2026-02-<auto>")
    assert scope == "INV-2026-02"
