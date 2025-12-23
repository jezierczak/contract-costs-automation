from pathlib import Path
import pandas as pd

import contract_costs.config as cfg

from contract_costs.model.contract import Contract
from contract_costs.model.cost_node import CostNode

class ContractStructureExcelGenerator:

    def generate(
        self,
        contract_row: dict | None,
        cost_node_rows: list[dict],
        output_path: Path,
    ) -> None:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

            if contract_row is None:
                pd.DataFrame(columns=self._contract_headers()).to_excel(
                    writer,
                    sheet_name=cfg.CONTRACT_METADATA_SHEET_NAME,
                    index=False,
                )
            else:
                pd.DataFrame([contract_row]).to_excel(
                    writer,
                    sheet_name=cfg.CONTRACT_METADATA_SHEET_NAME,
                    index=False,
                )

            pd.DataFrame(
                cost_node_rows,
                columns=self._cost_node_headers(),
            ).to_excel(
                writer,
                sheet_name=cfg.CONTRACT_ITEMS_SHEET_NAME,
                index=False,
            )

    @staticmethod
    def _contract_headers() -> list[str]:
        return [
            "code",
            "name",
            "owner_nip",
            "client_nip",
            "description",
            "start_date",
            "end_date",
            "budget",
            "path",
            "status",
        ]

    @staticmethod
    def _cost_node_headers() -> list[str]:
        return [
            "code",
            "name",
            "parent_code",
            "budget",
            "quantity",
            "unit",
            "is_active"
        ]


    @staticmethod
    def map_contract_to_row( contract: Contract) -> dict:
        return {
            "code": contract.code,
            "name": contract.name,
            "owner_nip": contract.owner.tax_number,
            "client_nip": contract.client.tax_number,
            "description": contract.description,
            "start_date": contract.start_date,
            "end_date": contract.end_date,
            "budget": contract.budget,
            "path": str(contract.path),
            "status": contract.status.name,
        }
    @staticmethod
    def flatten_cost_nodes(nodes: list[CostNode]) -> list[dict]:
        node_by_id = {node.id: node for node in nodes}
        rows = []

        for node in nodes:
            parent_code = None
            if node.parent_id:
                parent = node_by_id.get(node.parent_id)
                parent_code = parent.code if parent else None

            rows.append({
                "code": node.code,
                "name": node.name,
                "parent_code": parent_code,
                "budget": node.budget,
                "quantity": node.quantity,
                "unit": node.unit.value if node.unit else None,
                "is_active": node.is_active,
            })

        return rows

