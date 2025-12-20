from dataclasses import replace

from contract_costs.repository.inmemory.cost_type_repository import InMemoryCostTypeRepository


class TestInMemoryCostTypeRepository:

    def test_cost_type_repository_add_and_get(self, cost_type_material):
        repo = InMemoryCostTypeRepository()

        repo.add(cost_type_material)
        result = repo.get(cost_type_material.id)

        assert result == cost_type_material

    def test_cost_type_repository_exists(self, cost_type_material):
        repo = InMemoryCostTypeRepository()

        assert repo.exists(cost_type_material.id) is False

        repo.add(cost_type_material)

        assert repo.exists(cost_type_material.id) is True

    def test_cost_type_repository_get_by_code(
            self,
            cost_type_material,
            cost_type_service,
    ):
        repo = InMemoryCostTypeRepository()

        repo.add(cost_type_material)
        repo.add(cost_type_service)

        result = repo.get_by_code("MAT")

        assert result is not None
        assert result.id == cost_type_material.id
        assert result.code == "MAT"

    def test_cost_type_repository_list(
            self,
            cost_type_material,
            cost_type_service,
    ):
        repo = InMemoryCostTypeRepository()

        repo.add(cost_type_material)
        repo.add(cost_type_service)

        result = repo.list()

        assert len(result) == 2
        assert cost_type_material in result
        assert cost_type_service in result

    from dataclasses import replace

    def test_cost_type_repository_update(self, cost_type_material):
        repo = InMemoryCostTypeRepository()
        repo.add(cost_type_material)

        updated = replace(cost_type_material, name="Updated Material")
        repo.update(updated)

        result = repo.get(cost_type_material.id)

        assert result.name == "Updated Material"




