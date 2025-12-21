import builtins
from unittest.mock import MagicMock

from contract_costs.cli.commands.add_cost_type import handle_add_cost_type


def test_handle_add_cost_type_happy_path(monkeypatch):
    # --- mock interactive_prompt ---
    monkeypatch.setattr(
        "contract_costs.cli.commands.add_cost_type.interactive_prompt",
        lambda _: {
            "code": "MAT",
            "name": "Material",
            "description": "Material costs",
            "is_active": True,
        },
    )

    # --- mock input (confirm) ---
    inputs = iter(["y"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # --- mock services ---
    services = MagicMock()
    services.create_cost_type = MagicMock()

    monkeypatch.setattr(
        "contract_costs.cli.commands.add_cost_type.get_services",
        lambda: services,
    )

    # --- execute ---
    handle_add_cost_type()

    # --- assert ---
    services.create_cost_type.execute.assert_called_once_with(
        code="MAT",
        name="Material",
        description="Material costs",
        is_active=True,
    )

def test_handle_add_cost_type_cancel(monkeypatch):
    monkeypatch.setattr(
        "contract_costs.cli.commands.add_cost_type.interactive_prompt",
        lambda _: {
            "code": "MAT",
            "name": "Material",
            "description": None,
            "is_active": True,
        },
    )

    inputs = iter(["n"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    services = MagicMock()
    services.create_cost_type = MagicMock()

    monkeypatch.setattr(
        "contract_costs.cli.commands.add_cost_type.get_services",
        lambda: services,
    )

    handle_add_cost_type()

    services.create_cost_type.execute.assert_not_called()


