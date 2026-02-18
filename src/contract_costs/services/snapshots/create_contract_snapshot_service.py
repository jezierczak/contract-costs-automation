from datetime import datetime
from uuid import UUID

from decimal import Decimal
from collections import defaultdict
from typing import Dict, Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot
from contract_costs.model.snapshot.contract_node_snapshot import ContractNodeSnapshot
from contract_costs.model.snapshot.contract_node_value_snapshot import (
    ContractNodeValueSnapshot,
)
from contract_costs.services.contracts.prepare.contract_node_tree_index import (
    ContractNodeTreeIndex,
)
from contract_costs.services.snapshots.dto.create_contract_snapshot_command import CreateContractSnapshotCommand
from contract_costs.unit_of_work import UnitOfWork


class CreateContractSnapshotService(
    ActionHandler[CreateContractSnapshotCommand, tuple[ContractSnapshot, bool]]
):

    def __init__(
            self,
            *,
            id_generator: Callable[[], UUID] = new_uuid,
            clock: Callable[[], datetime] = utc_now,
    ):
        self._id_generator = id_generator
        self._clock = clock

    # =====================================================
    # PUBLIC API
    # =====================================================

    def execute(
            self,
            *,
            action: CreateContractSnapshotCommand,
            uow: UnitOfWork,
    ) -> tuple[ContractSnapshot, bool]:
        snapshot_repo = uow.contract_snapshots
        node_snapshot_repo = uow.contract_node_snapshots
        value_snapshot_repo = uow.contract_node_value_snapshots
        contract_repo = uow.contracts
        contract_node_repo = uow.contract_nodes
        line_record_repo = uow.financial_record_lines
        # ---------- idempotency ----------
        existing = snapshot_repo.get_by_contract_and_date(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
            snapshot_date=action.snapshot_date,
        )
        if existing:
            return existing, False

        # ---------- load contract ----------
        contract = contract_repo.get(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )
        if not contract:
            raise ValueError(f"Contract {action.contract_id} not found")

        # ---------- load nodes ----------
        nodes = contract_node_repo.list_by_contract(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )
        tree = ContractNodeTreeIndex(nodes)

        # ---------- load invoice lines ----------
        invoice_lines = line_record_repo.list_by_contract_until(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
            snapshot_date=action.snapshot_date,
        )

        # ---------- create snapshot root ----------
        snapshot = ContractSnapshot(
            id=self._id_generator(),
            organization_id=action.organization_id,
            contract_id=action.contract_id,
            snapshot_date=action.snapshot_date,
            created_at=self._clock(),
            created_by_user_id=action.actor_user_id,
        )

        # ==================================================
        # AGGREGATION STRUCTURES
        # ==================================================

        planned_budget: Dict[UUID, Decimal] = {}
        progress: Dict[UUID, Decimal] = {}

        values: Dict[
            UUID,
            Dict[
                UUID,
                Dict[str, Decimal]
            ]
        ] = defaultdict(
            lambda: defaultdict(
                lambda: {
                    "net": Decimal("0"),
                    "vat": Decimal("0"),
                    "gross": Decimal("0"),
                    "non_deductible": Decimal("0"),
                }
            )
        )

        # ==================================================
        # LEAF INITIALIZATION
        # ==================================================

        for node in tree.leaves():
            planned_budget[node.id] = node.budget or Decimal("0")

            p = node.progress_at(action.snapshot_date)
            progress[node.id] = p if p is not None else Decimal("0")

        # ==================================================
        # PROPAGATE PLANNED + PROGRESS UP
        # ==================================================

        for node in tree.postorder():
            if tree.is_leaf(node):
                continue

            children = tree.children_of(node.id)

            total_planned = sum(
                (planned_budget[c.id] for c in children),
                Decimal("0"),
            )
            planned_budget[node.id] = total_planned

            if total_planned > 0:
                weighted = sum(
                    (
                        planned_budget[c.id] * progress[c.id]
                        for c in children
                    ),
                    Decimal("0"),
                )
                progress[node.id] = weighted / total_planned
            else:
                progress[node.id] = Decimal("0")

        # ==================================================
        # AGGREGATE INVOICE LINES (LEAVES)
        # ==================================================

        for line in invoice_lines:
            if (
                line.contract_node_id is None
                or line.value_type_id is None
                or line.amount is None
            ):
                continue

            node_id = line.contract_node_id
            vt = line.value_type_id
            amount = line.amount

            v = values[node_id][vt]
            v["net"] += amount.net
            v["vat"] += amount.tax
            v["gross"] += amount.gross
            v["non_deductible"] += amount.non_tax_cost

        # ==================================================
        # PROPAGATE VALUES UP THE TREE
        # ==================================================

        for node in tree.postorder():
            if tree.is_leaf(node):
                continue

            for child in tree.children_of(node.id):
                for vt, child_vals in values[child.id].items():
                    parent_vals = values[node.id][vt]
                    parent_vals["net"] += child_vals["net"]
                    parent_vals["vat"] += child_vals["vat"]
                    parent_vals["gross"] += child_vals["gross"]
                    parent_vals["non_deductible"] += child_vals["non_deductible"]

        # ==================================================
        # BUILD SNAPSHOT ROWS
        # ==================================================

        node_snapshots: list[ContractNodeSnapshot] = []
        value_snapshots: list[ContractNodeValueSnapshot] = []

        node_snapshot_by_node: Dict[UUID, ContractNodeSnapshot] = {}

        for node in tree.all_nodes():
            ns = ContractNodeSnapshot(
                id=self._id_generator(),
                snapshot_id=snapshot.id,
                contract_node_id=node.id,
                planned_budget=planned_budget.get(node.id, Decimal("0")),
                progress=progress.get(node.id, Decimal("0")),
            )
            node_snapshot_by_node[node.id] = ns
            node_snapshots.append(ns)

        for node_id, vt_map in values.items():
            ns = node_snapshot_by_node[node_id]
            for vt, v in vt_map.items():
                value_snapshots.append(
                    ContractNodeValueSnapshot(
                        id=self._id_generator(),
                        node_snapshot_id=ns.id,
                        value_type_id=vt,
                        net=v["net"],
                        vat=v["vat"],
                        gross=v["gross"],
                        non_deductible=v["non_deductible"],
                    )
                )

        # ==================================================
        # PERSIST (TRANSACTIONAL – infra)
        # ==================================================

        snapshot_repo.add(snapshot)
        node_snapshot_repo.add_many(node_snapshots)
        value_snapshot_repo.add_many(value_snapshots)

        return snapshot, True
