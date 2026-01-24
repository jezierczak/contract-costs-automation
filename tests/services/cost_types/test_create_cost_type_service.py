from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.value_types.create_value_type_service import (
    CreateValueTypeService,
)
import pytest
from uuid import uuid4

from contract_costs.model.value_type import ValueType
from contract_costs.repository.inmemory.value_type_repository import (
    InMemoryValueTypeRepository,
)
from contract_costs.services.value_types.value_type_service import ValueTypeService


# ---------- fixtures ----------

@pytest.fixture
def repo():
    return InMemoryValueTypeRepository()


@pytest.fixture
def service(repo):
    return ValueTypeService(repo)


@pytest.fixture
def value_type_material():
    return ValueType(
        id=uuid4(),
        code="MATERIAL",
        name="Materiały",
        description="Koszty materiałów",
        direction=ValueDirection.COST,
        is_active=True,
    )


def test_create_value_type_success():
    repo = InMemoryValueTypeRepository()
    service = CreateValueTypeService(repo)

    service.execute(
        code="MAT",
        name="Material",
        description="Material costs",
        direction=ValueDirection.COST,
        is_active=True,
    )

    ct = repo.get_by_code("MAT")
    assert ct is not None
    assert ct.name == "Material"


def test_create_value_type_duplicate_code():
    repo = InMemoryValueTypeRepository()
    service = CreateValueTypeService(repo)

    service.execute(
        code="MAT",
        name="Material",
        description=None,
        direction=ValueDirection.COST,
        is_active=True,
    )

    with pytest.raises(ValueError):
        service.execute(
            code="MAT",
            name="Material v2",
            description=None,
            direction=ValueDirection.COST,
            is_active=True,
        )



# ---------- add ----------

def test_add_cost_type(service, repo, value_type_material):
    service.add(value_type_material)

    saved = repo.get_by_code("MATERIAL")
    assert saved is not None
    assert saved.name == "Materiały"
    assert saved.is_active is True


def test_add_duplicate_code_raises(service, value_type_material):
    service.add(value_type_material)

    with pytest.raises(ValueError, match="Value type with this code already exists"):
        service.add(
            ValueType(
                id=uuid4(),
                code="MATERIAL",  # ❌ ten sam code
                name="Inne",
                direction=ValueDirection.COST,
                description=None,
            )
        )


# ---------- rename ----------

def test_rename_cost_type(service, repo, value_type_material):
    repo.add(value_type_material)

    service.rename(value_type_material.id, "Nowa nazwa")

    updated = repo.get(value_type_material.id)
    assert updated.name == "Nowa nazwa"


def test_rename_non_existing_raises(service):
    with pytest.raises(ValueError, match="Value type does not exist"):
        service.rename(uuid4(), "X")


# ---------- deactivate ----------

def test_deactivate_cost_type(service, repo, value_type_material):
    repo.add(value_type_material)

    service.deactivate(value_type_material.id)

    updated = repo.get(value_type_material.id)
    assert updated.is_active is False


def test_deactivate_non_existing_raises(service):
    with pytest.raises(ValueError, match="Value type does not exist"):
        service.deactivate(uuid4())