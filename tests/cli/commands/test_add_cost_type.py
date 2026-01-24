import builtins
from unittest.mock import MagicMock

from contract_costs.cli.commands.add.add_value_type import handle_add_value_type
from contract_costs.model.value_direction import ValueDirection


def test_handle_add_value_type_happy_path(monkeypatch):
    # --- mock interactive_prompt ---
    monkeypatch.setattr(
        "contract_costs.cli.commands.add.add_value_type.interactive_prompt",
        lambda _: {
            "code": "MAT",
            "name": "Material",
            "description": "Material costs",
            "direction":"C",
            "is_active": True,
        },
    )

    # --- mock input (confirm) ---
    inputs = iter(["y"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # --- mock services ---
    services = MagicMock()
    services.create_value_type = MagicMock()

    monkeypatch.setattr(
        "contract_costs.cli.commands.add.add_value_type.get_services",
        lambda: services,
    )

    # --- execute ---
    handle_add_value_type()

    # --- assert ---
    services.create_value_type.execute.assert_called_once_with(
        code="MAT",
        name="Material",
        description="Material costs",
        direction=ValueDirection.COST,
        is_active=True,
    )

def test_handle_add_value_type_cancel(monkeypatch):
    monkeypatch.setattr(
        "contract_costs.cli.commands.add.add_value_type.interactive_prompt",
        lambda _: {
            "code": "MAT",
            "name": "Material",
            "description": None,
            "direction": "C",
            "is_active": True,
        },
    )

    inputs = iter(["n"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    services = MagicMock()
    services.create_value_type = MagicMock()

    monkeypatch.setattr(
        "contract_costs.cli.commands.add.add_value_type.get_services",
        lambda: services,
    )

    handle_add_value_type()

    services.create_value_type.execute.assert_not_called()


