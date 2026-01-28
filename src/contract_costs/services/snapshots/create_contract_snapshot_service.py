from uuid import uuid4, UUID
from datetime import date, datetime
from decimal import Decimal
from collections import defaultdict
from typing import Dict

from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot
from contract_costs.model.snapshot.contract_node_snapshot import ContractNodeSnapshot
from contract_costs.model.snapshot.contract_node_value_snapshot import (
    ContractNodeValueSnapshot,
)
from contract_costs.services.contracts.prepare.contract_node_tree_index import (
    ContractNodeTreeIndex,
)


class CreateContractSnapshotService:
    """
    Creates immutable snapshot of:
    - planned budgets
    - progress
    - aggregated financial values (net / vat / gross / non_deductible)
    """

    def __init__(
        self,
        *,
        contract_repo,
        contract_node_repo,
        invoice_line_repo,
        snapshot_repo,
        node_snapshot_repo,
        value_snapshot_repo,
    ) -> None:
        self._contract_repo = contract_repo
        self._node_repo = contract_node_repo
        self._invoice_repo = invoice_line_repo

        self._snapshot_repo = snapshot_repo
        self._node_snapshot_repo = node_snapshot_repo
        self._value_snapshot_repo = value_snapshot_repo

    # =====================================================
    # PUBLIC API
    # =====================================================

    def create(
        self,
        *,
        contract_id: UUID,
        snapshot_date: date,
    ) -> tuple[ContractSnapshot,bool]:

        # ---------- idempotency ----------
        existing = self._snapshot_repo.get_by_contract_and_date(
            contract_id=contract_id,
            snapshot_date=snapshot_date,
        )
        if existing:
            return existing, False

        contract = self._contract_repo.get(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")

        nodes = self._node_repo.list_by_contract(contract_id)
        tree = ContractNodeTreeIndex(nodes)

        invoice_lines = self._invoice_repo.list_by_contract_until(
            contract_id=contract_id,
            snapshot_date=snapshot_date,
        )

        snapshot = ContractSnapshot(
            id=uuid4(),
            contract_id=contract_id,
            snapshot_date=snapshot_date,
            created_at=datetime.now(),
        )

        # ==================================================
        # AGGREGATION STRUCTURES
        # ==================================================

        planned_budget: Dict[UUID, Decimal] = {}
        progress: Dict[UUID, Decimal] = {}

        # values[node_id][value_type_id] -> {net, vat, gross, non_deductible}
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

            p = node.progress_at(snapshot_date)
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
                id=uuid4(),
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
                        id=uuid4(),
                        node_snapshot_id=ns.id,
                        value_type_id=vt,
                        net=v["net"],
                        vat=v["vat"],
                        gross=v["gross"],
                        non_deductible=v["non_deductible"],
                    )
                )

        # ==================================================
        # PERSIST (SINGLE TRANSACTION)
        # ==================================================

        self._snapshot_repo.add(snapshot)
        self._node_snapshot_repo.add_many(node_snapshots)
        self._value_snapshot_repo.add_many(value_snapshots)

        return snapshot, True
