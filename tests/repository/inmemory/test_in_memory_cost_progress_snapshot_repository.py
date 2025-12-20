from decimal import Decimal

from contract_costs.repository.inmemory.cost_progress_snapshot_repository import InMemoryCostProgressSnapshotRepository


class TestInMemoryCostProgressSnapshotRepository:

    def test_cost_progress_snapshot_repository_add_and_get_by_contract(
            self,
            contract_id,
            snapshot_1,
            snapshot_other_node,
    ):
        repo = InMemoryCostProgressSnapshotRepository()

        repo.add(snapshot_1)
        repo.add(snapshot_other_node)

        result = repo.get_by_contract(contract_id)

        assert len(result) == 2
        assert snapshot_1 in result
        assert snapshot_other_node in result

    def test_cost_progress_snapshot_repository_get_latest(
            self,
            contract_id,
            cost_node_id,
            snapshot_1,
            snapshot_2,
    ):
        repo = InMemoryCostProgressSnapshotRepository()

        repo.add(snapshot_1)
        repo.add(snapshot_2)

        latest = repo.get_latest(contract_id, cost_node_id)

        assert latest is not None
        assert latest.id == snapshot_2.id
        assert latest.progress_percent == Decimal("0.50")

    def test_cost_progress_snapshot_repository_get_latest_returns_none(
            self,
            contract_id,
            cost_node_id,
    ):
        repo = InMemoryCostProgressSnapshotRepository()

        result = repo.get_latest(contract_id, cost_node_id)

        assert result is None

    def test_cost_progress_snapshot_repository_get_latest_for_contract_level(
            self,
            contract_id,
            snapshot_other_node,
    ):
        repo = InMemoryCostProgressSnapshotRepository()

        repo.add(snapshot_other_node)

        latest = repo.get_latest(contract_id, None)

        assert latest is not None
        assert latest.cost_node_id is None



