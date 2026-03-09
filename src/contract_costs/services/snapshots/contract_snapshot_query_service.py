from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.snapshot.contract_snapshot_repository import ContractSnapshotRepository
from contract_costs.services.snapshots.dto.contract_snapshot_dto import ContractSnapshotDTO, ContractNodeSnapshotDTO
from contract_costs.services.snapshots.dto.contract_snapshot_list_dto import ContractSnapshotListDTO
from contract_costs.services.snapshots.dto.contract_snapshot_query import BaseContractSnapshotQuery, \
    ListContractSnapshotsQuery, GetContractSnapshotQuery
from contract_costs.unit_of_work import UnitOfWork


class ContractSnapshotQueryService(
    ActionHandler[BaseContractSnapshotQuery, object]
):

    def execute(self, *, action:BaseContractSnapshotQuery, uow:UnitOfWork):

        if isinstance(action, ListContractSnapshotsQuery):
            return self._handle_list(action, uow)

        if isinstance(action, GetContractSnapshotQuery):
            return self._handle_get(action, uow)

        raise ValueError(f"Unsupported query type: {type(action)}")

    @staticmethod
    def _handle_list(
            action_list:ListContractSnapshotsQuery,
            uow:UnitOfWork,
    ) -> list[ContractSnapshotListDTO]:
        snapshot_repo = uow.contract_snapshots
        contract_repo = uow.contracts
        node_snapshot_repo = uow.contract_node_snapshots
        value_snapshot_repo = uow.contract_node_value_snapshots
        value_type_repo = uow.value_types

        value_types = value_type_repo.list_all(organization_id=action_list.organization_id)

        value_type_by_id = {
            vt.id: vt
            for vt in value_types
        }

        snapshots = (
            snapshot_repo.list_by_contract(
                organization_id=action_list.organization_id,
                contract_id=action_list.contract_id)
            if action_list.contract_id
            else snapshot_repo.list_all(organization_id=action_list.organization_id)
        )

        result: list[ContractSnapshotListDTO] = []

        for s in snapshots:
            contract = contract_repo.get(
                organization_id=action_list.organization_id,
                contract_id=s.contract_id)
            if not contract:
                continue

            # --- ROOT node snapshot ---
            root_node_snapshot = (
                node_snapshot_repo.get_root_by_snapshot(s.id)
            )
            if not root_node_snapshot:
                continue

            # --- VALUES for ROOT ---
            values = value_snapshot_repo.list_by_node_snapshot(
                root_node_snapshot.id
            )

            net_cost = Decimal("0")
            gross_cost = Decimal("0")
            non_deductible = Decimal("0")
            revenue = Decimal("0")

            for v in values:
                vt = value_type_by_id.get(v.value_type_id)
                if not vt:
                    continue

                match vt.direction:
                    case ValueDirection.COST:
                        net_cost += v.net
                        gross_cost += v.gross
                        non_deductible += v.non_deductible

                    case ValueDirection.REVENUE:
                        revenue += v.net

                    case _:
                        pass  # INTERNAL / inne – jawnie ignorowane

            result.append(
                ContractSnapshotListDTO(
                    snapshot_id=s.id,
                    snapshot_date=s.snapshot_date,
                    contract_id=contract.id,
                    contract_code=contract.code,
                    planned_budget=root_node_snapshot.planned_budget,
                    progress=root_node_snapshot.progress,
                    net_cost=net_cost,
                    gross_cost=gross_cost,
                    non_deductible=non_deductible,
                    revenue=revenue,
                )
            )

        return result

    def _handle_get(
            self,
            action_get:GetContractSnapshotQuery,
            uow:UnitOfWork
    ) -> ContractSnapshotDTO:
        snapshot_repo = uow.contract_snapshots
        node_snapshot_repo = uow.contract_node_snapshots
        value_snapshot_repo = uow.contract_node_value_snapshots
        contract_repo = uow.contracts
        node_repo = uow.contract_nodes
        value_type_repo = uow.value_types

        snapshot = self.resolve_snapshot(
            organization_id=action_get.organization_id,
            prefix=str(action_get.snapshot_id_prefix),
            repo=snapshot_repo,
        )
        if not snapshot:
            raise ValueError("Snapshot not found")
        snapshot_id = snapshot.id

        contract = contract_repo.get(
            organization_id=action_get.organization_id,
            contract_id=snapshot.contract_id)
        nodes = node_repo.list_by_contract(
            organization_id=action_get.organization_id,
            contract_id=snapshot.contract_id)

        node_snapshots = node_snapshot_repo.list_by_snapshot(snapshot_id)
        value_snapshots = value_snapshot_repo.list_by_snapshot(snapshot_id)

        nodes_by_id = {n.id: n for n in nodes}
        values_by_node_snapshot = defaultdict(list)

        value_types = value_type_repo.list_all(organization_id=action_get.organization_id)
        value_type_by_id = {vt.id: vt for vt in value_types}

        for v in value_snapshots:
            values_by_node_snapshot[v.node_snapshot_id].append(v)

        result_nodes: list[ContractNodeSnapshotDTO] = []

        for ns in node_snapshots:
            node = nodes_by_id[ns.contract_node_id]
            values = values_by_node_snapshot.get(ns.id, [])
            net_cost = Decimal("0")
            vat = Decimal("0")
            gross = Decimal("0")
            non_deductible = Decimal("0")
            revenue = Decimal("0")
            revenue_non_deductible = Decimal("0")

            for v in values:
                vt = value_type_by_id.get(v.value_type_id)
                if not vt:
                    continue

                if vt.direction == ValueDirection.COST:
                    net_cost += v.amount_value
                    vat += v.vat
                    gross += v.gross
                    non_deductible += v.non_deductible

                elif vt.direction == ValueDirection.REVENUE:
                    revenue += v.amount_value
                    revenue_non_deductible += v.non_deductible

            result_nodes.append(
                ContractNodeSnapshotDTO(
                    node_id=node.id,
                    parent_id=node.parent_id,
                    code=node.code,
                    name=node.name,
                    level=node.level if hasattr(node, "level") else 0,
                    planned_budget=ns.planned_budget,
                    progress=ns.progress,
                    net=net_cost,
                    vat=vat,
                    gross=gross,
                    non_deductible=non_deductible,
                    revenue=revenue,
                    revenue_non_deductible=revenue_non_deductible
                )
            )

        if not contract:
            raise ValueError("Contract not found")

        return ContractSnapshotDTO(
            snapshot_id=snapshot.id,
            contract_code=contract.code,
            snapshot_date=snapshot.snapshot_date,
            nodes=result_nodes,
        )

    @staticmethod
    def resolve_snapshot(
            *,
            organization_id: UUID,
            prefix: str,
            repo: ContractSnapshotRepository,
    ) -> ContractSnapshot:

        snapshots = repo.list_all(organization_id=organization_id)

        matches = [
            snap for snap in snapshots
            if str(snap.id).startswith(prefix)
        ]

        if not matches:
            raise ValueError(f"No snapshot found for '{prefix}'")

        if len(matches) > 1:
            ids = ", ".join(str(s.id)[:8] for s in matches)
            raise ValueError(
                f"Snapshot id '{prefix}' is ambiguous. Matches: {ids}"
            )

        return matches[0]
