from pathlib import Path
from typing import Any

from contract_costs.infrastructure.excel.base_excel_exporter import BaseExcelExporter
from contract_costs.infrastructure.excel.contracts.contract_node_progress_prepare_columns import \
    CONTRACT_NODE_PROGRESS_PREPARE_COLUMNS
from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode
import contract_costs.config as cfg
from contract_costs.services.contracts.prepare.mappers.contract_node_progress_prepare_mapper import \
    ContractNodeProgressPrepareMapper


class ContractPrepareProgressExcelExporter:
    """
    Prepare Contract Progress Excel (LEAFS ONLY).

    - EDIT only
    - shows current progress (%)
    - empty column for new progress (%)

    Excel is source of truth for apply-progress.
    """

    COST_NODES_SHEET = cfg.CONTRACT_ITEMS_SHEET_NAME

    # =====================================================
    # PUBLIC API
    # =====================================================

    def export_existing(
        self,
        *,
        contract: Contract,
        cost_nodes: list[ContractNode],
        output_path: Path,
    ) -> None:
        exporter = BaseExcelExporter[Any]()

        cost_node_dtos = (
            ContractNodeProgressPrepareMapper.map(
                contract=contract,
                nodes=cost_nodes
            )
            if cost_nodes else []
        )

        exporter.add_sheet(
            sheet_name=self.COST_NODES_SHEET,
            items=cost_node_dtos,
            columns=CONTRACT_NODE_PROGRESS_PREPARE_COLUMNS,
        )

        exporter.save(output_path)
