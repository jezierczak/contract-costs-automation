from dataclasses import replace

from contract_costs.repository.inmemory.value_type_repository import InMemoryValueTypeRepository


class TestInMemoryCostTypeRepository:

    def test_cost_type_repository_add_and_get(self, value_type_material):
        repo = InMemoryValueTypeRepository()

        repo.add(value_type_material)
        result = repo.get(value_type_material.id)

        assert result == value_type_material

    def test_cost_type_repository_exists(self, value_type_material):
        repo = InMemoryValueTypeRepository()

        assert repo.exists(value_type_material.id) is False

        repo.add(value_type_material)

        assert repo.exists(value_type_material.id) is True

    def test_cost_type_repository_get_by_code(
            self,
            value_type_material,
            value_type_service,
    ):
        repo = InMemoryValueTypeRepository()

        repo.add(value_type_material)
        repo.add(value_type_service)

        result = repo.get_by_code("MAT")

        assert result is not None
        assert result.id == value_type_material.id
        assert result.code == "MAT"

    def test_cost_type_repository_list(
            self,
            value_type_material,
            value_type_service,
    ):
        repo = InMemoryValueTypeRepository()

        repo.add(value_type_material)
        repo.add(value_type_service)

        result = repo.list()

        assert len(result) == 2
        assert value_type_material in result
        assert value_type_service in result

    from dataclasses import replace

    def test_cost_type_repository_update(self, value_type_material):
        repo = InMemoryValueTypeRepository()
        repo.add(value_type_material)

        updated = replace(value_type_material, name="Updated Material")
        repo.update(updated)

        result = repo.get(value_type_material.id)

        assert result.name == "Updated Material"




