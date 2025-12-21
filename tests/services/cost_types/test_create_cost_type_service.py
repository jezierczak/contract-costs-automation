import pytest

from contract_costs.repository.inmemory.cost_type_repository import (
    InMemoryCostTypeRepository,
)
from contract_costs.services.cost_types.create_cost_type_service import (
    CreateCostTypeService,
)


def test_create_cost_type_success():
    repo = InMemoryCostTypeRepository()
    service = CreateCostTypeService(repo)

    service.execute(
        code="MAT",
        name="Material",
        description="Material costs",
        is_active=True,
    )

    ct = repo.get_by_code("MAT")
    assert ct is not None
    assert ct.name == "Material"


def test_create_cost_type_duplicate_code():
    repo = InMemoryCostTypeRepository()
    service = CreateCostTypeService(repo)

    service.execute(
        code="MAT",
        name="Material",
        description=None,
        is_active=True,
    )

    with pytest.raises(ValueError):
        service.execute(
            code="MAT",
            name="Material v2",
            description=None,
            is_active=True,
        )
