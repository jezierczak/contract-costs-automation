from unittest.mock import MagicMock
from contract_costs.cli.adapters.cost_type_adapter import create_cost_type_from_cli


def test_create_cost_type_from_cli():
    data = {
        "code": "MAT",
        "name": "Material",
        "description": "Material costs",
        "is_active": True,
    }

    service = MagicMock()

    create_cost_type_from_cli(
        data=data,
        create_cost_type_service=service,
    )

    service.execute.assert_called_once_with(
        code="MAT",
        name="Material",
        description="Material costs",
        is_active=True,
    )
