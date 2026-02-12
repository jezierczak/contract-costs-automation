from unittest.mock import MagicMock
from contract_costs.cli.adapters.value_type_adapter import create_value_type_from_cli
from contract_costs.model.value_direction import ValueDirection


def test_create_cost_type_from_cli():
    data = {
        "code": "MAT",
        "name": "Material",
        "description": "Material costs",
        "direction": "C",
        "is_active": True,
    }

    service = MagicMock()

    create_value_type_from_cli(
        data=data,
        create_value_type_service=service,
    )

    service.execute.assert_called_once_with(
        code="MAT",
        name="Material",
        description="Material costs",
        direction=ValueDirection.COST,
        is_active=True,
    )
