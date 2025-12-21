from decimal import Decimal

import pytest

from contract_costs.builders.cost_node_tree_builder import DefaultCostNodeTreeBuilder
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository
from contract_costs.services.contracts.create_contract_service import CreateContractService


class TestCreateContractService:

    def test_create_contract_execute_not_initialized(self,create_contract_service) -> None:

        with pytest.raises(RuntimeError, match="Contract not initialized"):
            create_contract_service.execute()

    def test_create_contract_add_nodes_not_initialized(self,create_contract_service,cost_node_tree_1) -> None:

        with pytest.raises(RuntimeError, match="Contract not initialized"):
            create_contract_service.add_cost_node_tree(cost_node_tree_1)


    def test_create_contract_without_nodes(self,contract_starter_1) -> None:
        con_repo = InMemoryContractRepository()
        node_repo = InMemoryCostNodeRepository()
        tree_builder = DefaultCostNodeTreeBuilder()
        service = CreateContractService(
            contract_repository=con_repo,
            cost_node_repository=node_repo, cost_node_tree_builder=tree_builder
        )

        service.init(contract_starter=contract_starter_1)
        service.execute()

        contracts = con_repo.list()
        assert len(contracts) == 1

        contract = contracts[0]

        # --- kluczowe pola kontraktu ---
        assert contract.name == contract_starter_1["name"]
        assert contract.description == contract_starter_1["description"]
        assert contract.budget == contract_starter_1["budget"]
        assert contract.start_date == contract_starter_1["start_date"]
        assert contract.end_date == contract_starter_1["end_date"]
        assert contract.path == contract_starter_1["path"]
        assert contract.status == contract_starter_1["status"]

        # --- relacje ---
        assert contract.owner == contract_starter_1["contract_owner"]
        assert contract.client == contract_starter_1["client"]

        # --- brak cost nodes ---
        assert node_repo.list_nodes() == []

    def test_create_contract_with_nodes(self, contract_starter_1,cost_node_tree_1) -> None:
        con_repo = InMemoryContractRepository()
        node_repo = InMemoryCostNodeRepository()
        tree_builder = DefaultCostNodeTreeBuilder()
        contract = CreateContractService(
            contract_repository=con_repo,
            cost_node_repository=node_repo, cost_node_tree_builder=tree_builder
        )

        contract.init(contract_starter=contract_starter_1)
        contract.add_cost_node_tree(cost_node_tree_1)
        contract.execute()

        # --- kontrakt ---
        contracts = con_repo.list()
        assert len(contracts) == 1
        contract = contracts[0]

        # --- cost nodes ---
        nodes = node_repo.list_nodes()
        assert len(nodes) == 3

        # --- kody ---
        codes = {n.code for n in nodes}
        assert codes == {"WYB", "WYB_SCI", "WYB_POS"}

        # --- wszystkie należą do kontraktu ---
        assert all(n.contract_id == contract.id for n in nodes)

        # --- root ---
        roots = [n for n in nodes if n.parent_id is None]
        assert len(roots) == 1

        root = roots[0]
        assert root.code == "WYB"
        assert root.budget == Decimal("100000")
        assert root.is_active is True

        # --- dzieci ---
        children = [n for n in nodes if n.parent_id == root.id]
        assert len(children) == 2

        child_codes = {c.code for c in children}
        assert child_codes == {"WYB_SCI", "WYB_POS"}

        # --- budżety dzieci ---
        budgets = {c.code: c.budget for c in children}
        assert budgets["WYB_SCI"] == Decimal("50000")
        assert budgets["WYB_POS"] == Decimal("50000")


