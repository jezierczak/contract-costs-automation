from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.snapshot.contract_node_snapshot_repository import ContractNodeSnapshotRepository
from contract_costs.repository.snapshot.contract_node_value_snapshot_repository import \
    ContractNodeValueSnapshotRepository
from contract_costs.repository.snapshot.contract_snapshot_repository import ContractSnapshotRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.snapshots.dto.contract_snapshot_dto import ContractSnapshotDTO, ContractNodeSnapshotDTO
from contract_costs.services.snapshots.dto.contract_snapshot_list_dto import ContractSnapshotListDTO

class ContractSnapshotQueryService:

    def __init__(
        self,
        *,
        contract_repo: ContractRepository,
        contract_node_repo: ContractNodeRepository,
        value_type_repo: ValueTypeRepository,
        snapshot_repo: ContractSnapshotRepository,
        node_snapshot_repo: ContractNodeSnapshotRepository,
        value_snapshot_repo:ContractNodeValueSnapshotRepository,
    ) -> None:
        self._contract_repo = contract_repo
        self._node_repo = contract_node_repo
        self._value_type_repo = value_type_repo
        self._snapshot_repo = snapshot_repo
        self._node_snapshot_repo = node_snapshot_repo
        self._value_snapshot_repo = value_snapshot_repo

    def list_snapshots(
            self,
            *,
            contract_id: UUID | None = None,
    ) -> list[ContractSnapshotListDTO]:
        value_types = self._value_type_repo.list()

        value_type_by_id = {
            vt.id: vt
            for vt in value_types
        }

        snapshots = (
            self._snapshot_repo.list_by_contract(contract_id)
            if contract_id
            else self._snapshot_repo.list_all()
        )

        result: list[ContractSnapshotListDTO] = []

        for s in snapshots:
            contract = self._contract_repo.get(s.contract_id)
            if not contract:
                continue

            # --- ROOT node snapshot ---
            root_node_snapshot = (
                self._node_snapshot_repo.get_root_by_snapshot(s.id)
            )
            if not root_node_snapshot:
                continue

            # --- VALUES for ROOT ---
            values = self._value_snapshot_repo.list_by_node_snapshot(
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

    def get_snapshot(
            self,
            *,
            snapshot_id: UUID,
    ) -> ContractSnapshotDTO:

        snapshot = self.resolve_snapshot(str(snapshot_id),self._snapshot_repo)
        if not snapshot:
            raise ValueError("Snapshot not found")
        snapshot_id = snapshot.id

        contract = self._contract_repo.get(snapshot.contract_id)
        nodes = self._node_repo.list_by_contract(snapshot.contract_id)

        node_snapshots = self._node_snapshot_repo.list_by_snapshot(snapshot_id)
        value_snapshots = self._value_snapshot_repo.list_by_snapshot(snapshot_id)

        nodes_by_id = {n.id: n for n in nodes}
        values_by_node_snapshot = defaultdict(list)

        value_types = self._value_type_repo.list()
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

            for v in values:
                vt = value_type_by_id.get(v.value_type_id)
                if not vt:
                    continue

                if vt.direction == ValueDirection.COST:
                    net_cost += v.net
                    vat += v.vat
                    gross += v.gross
                    non_deductible += v.non_deductible

                elif vt.direction == ValueDirection.REVENUE:
                    revenue += v.net

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
    def resolve_snapshot(prefix: str, repo) -> ContractSnapshot:
        # pełny UUID
        snapshots = repo.list_all()

        # def find_by_id_prefix(self, prefix: str) -> list[ContractSnapshot]:
        matches =  [snap for snap in snapshots if str(snap.id).startswith(prefix)]

        if not matches:
            raise ValueError(f"No snapshot found for '{prefix}'")

        if len(matches) > 1:
            ids = ", ".join(s.short_id for s in matches)
            raise ValueError(
                f"Snapshot id '{prefix}' is ambiguous. Matches: {ids}"
            )

        return matches[0]
