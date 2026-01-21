from pathlib import Path
from typing import Any

from contract_costs.infrastructure.excel.base_excel_exporter import (
    BaseExcelExporter,
)

from contract_costs.infrastructure.excel.contracts.contract_prepare_columns import (
    CONTRACT_PREPARE_COLUMNS,
)
from contract_costs.infrastructure.excel.contracts.cost_node_prepare_columns import (
    COST_NODE_PREPARE_COLUMNS,
)
import contract_costs.config as cfg

from contract_costs.model.contract import Contract
from contract_costs.model.cost_node import CostNode
from contract_costs.services.contracts.prepare.dto.contract_prepare_dto import ContractPrepareDTO
from contract_costs.services.contracts.prepare.mappers.contract_prepare_mapper import ContractPrepareMapper
from contract_costs.services.contracts.prepare.mappers.cost_node_prepare_mapper import CostNodePrepareMapper


class ContractPrepareExcelExporter:
    """
    Prepare Contract Excel (FULL EDIT).

    - NEW  -> empty sheets with headers
    - EDIT -> populated sheets

    Excel is source of truth for apply.
    """

    CONTRACT_SHEET = cfg.CONTRACT_METADATA_SHEET_NAME
    COST_NODES_SHEET = cfg.CONTRACT_ITEMS_SHEET_NAME

    # =====================================================
    # PUBLIC API
    # =====================================================

    def export_new(self, *, output_path: Path) -> None:
        exporter = BaseExcelExporter[Any]()

        exporter.add_sheet(
            sheet_name=self.CONTRACT_SHEET,
            items=[],
            columns=CONTRACT_PREPARE_COLUMNS,
        )

        exporter.add_sheet(
            sheet_name=self.COST_NODES_SHEET,
            items=[],
            columns=COST_NODE_PREPARE_COLUMNS,
        )

        exporter.save(output_path)

    def export_existing(
        self,
        *,
        contract: Contract,
        cost_nodes: list[CostNode],
        output_path: Path,
    ) -> None:
        exporter = BaseExcelExporter[Any]()

        contract_dtos = [
            ContractPrepareMapper.map(contract)
        ]
        cost_node_dtos = (
            CostNodePrepareMapper.map(cost_nodes)
            if cost_nodes else []
        )

        exporter.add_sheet(
            sheet_name=self.CONTRACT_SHEET,
            items=contract_dtos,
            columns=CONTRACT_PREPARE_COLUMNS,
        )

        exporter.add_sheet(
            sheet_name=self.COST_NODES_SHEET,
            items=cost_node_dtos,
            columns=COST_NODE_PREPARE_COLUMNS,
        )

        exporter.save(output_path)
