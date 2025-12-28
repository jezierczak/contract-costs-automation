from pathlib import Path
from uuid import UUID
from decimal import Decimal
from typing import Any

import pandas as pd

import contract_costs.config as cfg

from contract_costs.model.contract import ContractStarter, ContractStatus
from contract_costs.model.cost_node import CostNodeInput
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.contracts.update_contract_structure_service import (
    UpdateContractStructureService,
)

from contract_costs.services.invoices.company_resolve_service import CompanyResolveService


class ApplyContractStructureExcelService:
    """
    Orchestrator:
    - NEW contract (create)
    - EDIT existing contract (replace structure)

    Excel is the source of truth.
    """

    def __init__(
        self,
        create_contract_service: CreateContractService,
        update_contract_structure_service: UpdateContractStructureService,
        company_resolve_service: CompanyResolveService,
        # validator: CostNodeTreeValidator,
    ) -> None:
        self._create_contract = create_contract_service
        self._update_contract = update_contract_structure_service
        self._company_resolver = company_resolve_service
        # self._validator = validator

    # ===================== PUBLIC API =====================

    def apply_new(self, excel_path: Path) -> None:
        contract_starter, cost_node_tree = self._load_from_excel(excel_path)

        self._create_contract.init(contract_starter)
        self._create_contract.add_cost_node_tree(cost_node_tree)
        self._create_contract.execute()

    def apply_update(self, excel_path: Path, contract_id: UUID) -> None:
        contract_starter, cost_node_tree = self._load_from_excel(excel_path)

        # EDIT requires validation
        # self._validator.validate_forest(cost_node_tree)

        self._update_contract.execute(
            contract_id=contract_id,
            contract_starter=contract_starter,
            cost_node_input=cost_node_tree,
        )

    # ===================== LOADING =====================

    def _load_from_excel(
        self, path: Path
    ) -> tuple[ContractStarter, list[CostNodeInput]]:
        contract_row, cost_node_rows = self._read_excel(path)

        contract_row = self._normalize_row(contract_row)
        cost_node_rows = [self._normalize_row(r) for r in cost_node_rows]

        contract_starter = self._build_contract_starter(contract_row)
        cost_node_tree = self._build_cost_node_tree(cost_node_rows)

        return contract_starter, cost_node_tree

    @staticmethod
    def _read_excel(path: Path) -> tuple[dict, list[dict]]:
        with pd.ExcelFile(path) as xls:
            contract_df = pd.read_excel(
                xls,
                sheet_name=cfg.CONTRACT_METADATA_SHEET_NAME,
            )
            cost_nodes_df = pd.read_excel(
                xls,
                sheet_name=cfg.CONTRACT_ITEMS_SHEET_NAME,
            )

        if len(contract_df) != 1:
            raise ValueError("Contract metadata sheet must contain exactly one row")

        return (
            contract_df.iloc[0].to_dict(),
            cost_nodes_df.to_dict(orient="records"),
        )

    # ===================== NORMALIZATION =====================

    @staticmethod
    def _normalize_cell(value: Any) -> Any:
        if pd.isna(value):
            return None
        return value

    def _normalize_row(self, row: dict) -> dict:
        return {k: self._normalize_cell(v) for k, v in row.items()}

    # ===================== BUILDERS =====================

    def _build_contract_starter(self, row: dict) -> ContractStarter:
        owner = self._company_resolver.find_by_tax_number(row["owner_nip"])
        client = self._company_resolver.find_by_tax_number(row["client_nip"])

        return ContractStarter(
            name=row["name"],
            code=row["code"],
            contract_owner=owner,
            client=client,
            description=row.get("description"),
            start_date=row.get("start_date"),
            end_date=row.get("end_date"),
            budget=Decimal(str(row["budget"])) if row.get("budget") is not None else None,
            path=Path(row["path"]),
            status=ContractStatus[row["status"]],
        )

    @staticmethod
    def _build_cost_node_tree( rows: list[dict]) -> list[CostNodeInput]:
        nodes: dict[str, CostNodeInput] = {}

        # create nodes
        for row in rows:
            nodes[row["code"]] = {
                "code": row["code"],
                "name": row["name"],
                "budget": Decimal(str(row["budget"])) if row.get("budget") is not None else None,
                "quantity": Decimal(str(row["quantity"])) if row.get("quantity") is not None else None,
                "unit": ApplyContractStructureExcelService._map_unit(row.get("unit")),
                "children": [],
                "is_active": bool(row.get("is_active", True)),
            }

        # build hierarchy
        roots: list[CostNodeInput] = []

        for row in rows:
            node = nodes[row["code"]]
            parent_code = row.get("parent_code")

            if parent_code:
                if parent_code not in nodes:
                    raise ValueError(
                        f"Parent code '{parent_code}' not found for node '{row['code']}'"
                    )
                nodes[parent_code]["children"].append(node)
            else:
                roots.append(node)

        if not roots:
            raise ValueError("At least one root cost node is required")

        return roots

    @staticmethod
    def _map_unit(value):
        if pd.isna(value) or value is None:
            return None
        try:
            return UnitOfMeasure(value)
        except ValueError:
            raise ValueError(f"Invalid unit '{value}'")