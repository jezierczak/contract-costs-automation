from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from contract_costs.infrastructure.excel.contracts.contract_node_progress_prepare_columns import \
    CONTRACT_NODE_PROGRESS_PREPARE_COLUMNS
from contract_costs.infrastructure.excel.excel_loader import ExcelLoader
from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode
from contract_costs.repository.contract_node_repository import ContractNodeRepository
import contract_costs.config as cfg
from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex


class ApplyContractProgressExcelService:
    """
    Orchestrator:
    - applies progress updates to existing contract nodes
    - Excel is the source of truth for progress values
    """

    CONTRACT_PROGRESS_SHEET = cfg.CONTRACT_ITEMS_SHEET_NAME

    def __init__(
        self,
        contract_node_repository: ContractNodeRepository,
    ) -> None:
        self._node_repo = contract_node_repository

    def apply(
            self,
            *,
            contract: Contract,
            excel_path: Path,
    ) -> None:
        rows = self._load_from_excel(excel_path)

        self._apply_progress_rows(
            contract=contract,
            rows=rows,
        )

    def _load_from_excel(
            self,
            path: Path,
    ) -> list[dict[str, Any]]:
        rows = ExcelLoader.load(
            input_path=path,
            sheet_name=self.CONTRACT_PROGRESS_SHEET,
            columns=CONTRACT_NODE_PROGRESS_PREPARE_COLUMNS,
        )

        if not rows:
            raise ValueError("Progress sheet is empty")

        return rows

    def _apply_progress_rows(
            self,
            *,
            contract: Contract,
            rows: list[dict[str, Any]],
    ) -> None:

        nodes = self._node_repo.list_by_contract(contract.id)
        tree = ContractNodeTreeIndex(nodes)
        nodes_by_id = {n.id: n for n in nodes}

        updated_nodes: list[ContractNode] = []
        for row in rows:
            # --- contract safety ---
            if row["Contract"] != contract.code:
                raise ValueError(
                    f"Row contract '{row['Contract']}' "
                    f"does not match '{contract.code}'"
                )

            node_id = UUID(row["Node ID"])
            new_progress = row.get("New Progress [%]")

            # --- skip empty ---
            if new_progress is None:
                continue

            if not (Decimal("0") <= new_progress <= Decimal("100")):
                raise ValueError(
                    f"Invalid progress {new_progress} for node {row['Code']}"
                )

            node = nodes_by_id.get(node_id)
            if not node:
                raise ValueError(f"Contract node {node_id} not found")

            if node.contract_id != contract.id:
                raise ValueError(
                    f"Node {node.code} does not belong to contract {contract.code}"
                )

            # --- leaf only ---
            if not tree.is_leaf(node):
                raise ValueError(
                    f"Progress can be set only on leaf nodes ({node.code})"
                )

            if not node.is_active:
                continue  # albo raise – decyzja domenowa

            node.progress = new_progress / Decimal("100")
            updated_nodes.append(node)

        self._node_repo.update_many(updated_nodes)
