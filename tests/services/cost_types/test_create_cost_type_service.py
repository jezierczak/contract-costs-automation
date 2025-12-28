
from contract_costs.services.cost_types.create_cost_type_service import (
    CreateCostTypeService,
)
import pytest
from uuid import uuid4

from contract_costs.model.cost_type import CostType
from contract_costs.repository.inmemory.cost_type_repository import (
    InMemoryCostTypeRepository,
)
from contract_costs.services.cost_types.cost_type_service import CostTypeService


# ---------- fixtures ----------

@pytest.fixture
def repo():
    return InMemoryCostTypeRepository()


@pytest.fixture
def service(repo):
    return CostTypeService(repo)


@pytest.fixture
def cost_type_material():
    return CostType(
        id=uuid4(),
        code="MATERIAL",
        name="Materiały",
        description="Koszty materiałów",
        is_active=True,
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



# ---------- add ----------

def test_add_cost_type(service, repo, cost_type_material):
    service.add(cost_type_material)

    saved = repo.get_by_code("MATERIAL")
    assert saved is not None
    assert saved.name == "Materiały"
    assert saved.is_active is True


def test_add_duplicate_code_raises(service, cost_type_material):
    service.add(cost_type_material)

    with pytest.raises(ValueError, match="Cost type with this code already exists"):
        service.add(
            CostType(
                id=uuid4(),
                code="MATERIAL",  # ❌ ten sam code
                name="Inne",
                description=None,
            )
        )


# ---------- rename ----------

def test_rename_cost_type(service, repo, cost_type_material):
    repo.add(cost_type_material)

    service.rename(cost_type_material.id, "Nowa nazwa")

    updated = repo.get(cost_type_material.id)
    assert updated.name == "Nowa nazwa"


def test_rename_non_existing_raises(service):
    with pytest.raises(ValueError, match="Cost type does not exist"):
        service.rename(uuid4(), "X")


# ---------- deactivate ----------

def test_deactivate_cost_type(service, repo, cost_type_material):
    repo.add(cost_type_material)

    service.deactivate(cost_type_material.id)

    updated = repo.get(cost_type_material.id)
    assert updated.is_active is False


def test_deactivate_non_existing_raises(service):
    with pytest.raises(ValueError, match="Cost type does not exist"):
        service.deactivate(uuid4())