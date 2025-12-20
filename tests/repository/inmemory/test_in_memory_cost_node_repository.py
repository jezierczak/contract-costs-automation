from dataclasses import replace
from decimal import Decimal

from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository


class TestInMemoryCostNodeRepository:

    def test_cost_node_repository_add_and_get(self,root_node) -> None:
        repo = InMemoryCostNodeRepository()

        repo.add(root_node)
        result = repo.get(root_node.id)

        assert result == root_node

    def test_cost_node_repository_exists(self,root_node):
        repo = InMemoryCostNodeRepository()

        assert repo.exists(root_node.id) is False

        repo.add(root_node)

        assert repo.exists(root_node.id) is True

    def test_cost_node_repository_list_nodes(self,root_node, child_node):
        repo = InMemoryCostNodeRepository()

        repo.add(root_node)
        repo.add(child_node)

        nodes = repo.list_nodes()

        assert len(nodes) == 2
        assert root_node in nodes
        assert child_node in nodes

    def test_cost_node_repository_list_by_contract(self, root_node, child_node):
        repo = InMemoryCostNodeRepository()

        repo.add(root_node)
        repo.add(child_node)

        result = repo.list_by_contract(root_node.contract_id)

        assert len(result) == 2
        assert all(n.contract_id == root_node.contract_id for n in result)

    def test_cost_node_repository_list_by_parent(self, root_node, child_node):
        repo = InMemoryCostNodeRepository()

        repo.add(root_node)
        repo.add(child_node)

        children = repo.list_by_parent(root_node.id)

        assert len(children) == 1
        assert children[0].id == child_node.id


    def test_cost_node_repository_update(self, root_node):
        repo = InMemoryCostNodeRepository()
        repo.add(root_node)

        updated = replace(root_node, budget=Decimal("2000"))
        repo.update(updated)

        result = repo.get(root_node.id)

        assert result.budget == Decimal("2000")




