from pathlib import Path
from uuid import UUID
from decimal import Decimal
from typing import Any

import contract_costs.config as cfg

from contract_costs.infrastructure.excel.excel_loader import ExcelLoader
from contract_costs.infrastructure.excel.contracts.contract_prepare_columns import (
    CONTRACT_PREPARE_COLUMNS,
)
from contract_costs.infrastructure.excel.contracts.cost_node_prepare_columns import (
    COST_NODE_PREPARE_COLUMNS,
)

from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractStarter, ContractStatus
from contract_costs.model.cost_node import CostNodeInput
from contract_costs.model.unit_of_measure import UnitOfMeasure

from contract_costs.services.companies.company_evaluate_orchestrator import (
    CompanyEvaluateOrchestrator,
)
from contract_costs.services.contracts.create_contract_service import (
    CreateContractService,
)
from contract_costs.services.contracts.apply.update_contract_structure_service import (
    UpdateContractStructureService,
)


class ApplyContractStructureExcelService:
    """
    Orchestrator:
    - NEW contract (create)
    - EDIT existing contract (replace structure)

    Excel is the source of truth.
    """

    CONTRACT_SHEET = cfg.CONTRACT_METADATA_SHEET_NAME
    COST_NODES_SHEET = cfg.CONTRACT_ITEMS_SHEET_NAME


    def __init__(
        self,
        create_contract_service: CreateContractService,
        update_contract_structure_service: UpdateContractStructureService,
        company_evaluate_orchestrator: CompanyEvaluateOrchestrator,
    ) -> None:
        self._create_contract = create_contract_service
        self._update_contract = update_contract_structure_service
        self._company_eval = company_evaluate_orchestrator

    # =====================================================
    # PUBLIC API
    # =====================================================

    def apply_new(self, excel_path: Path) -> None:
        starter, cost_nodes = self._load_from_excel(excel_path)

        self._create_contract.init(starter)
        self._create_contract.add_cost_node_tree(cost_nodes)
        self._create_contract.execute()

    def apply_update(self, *, excel_path: Path, contract_id: UUID) -> None:
        starter, cost_nodes = self._load_from_excel(excel_path)

        self._update_contract.execute(
            contract_id=contract_id,
            contract_starter=starter,
            cost_node_input=cost_nodes,
        )

    # =====================================================
    # LOADING
    # =====================================================

    def _load_from_excel(
        self,
        path: Path,
    ) -> tuple[ContractStarter, list[CostNodeInput]]:

        contract_rows = ExcelLoader.load(
            input_path=path,
            sheet_name=self.CONTRACT_SHEET,
            columns=CONTRACT_PREPARE_COLUMNS,
        )
        print(contract_rows)
        if len(contract_rows) != 1:
            raise ValueError(
                "Contract sheet must contain exactly one row"
            )

        cost_node_rows = ExcelLoader.load(
            input_path=path,
            sheet_name=self.COST_NODES_SHEET,
            columns=COST_NODE_PREPARE_COLUMNS,
        )

        starter = self._build_contract_starter(contract_rows[0])
        cost_node_tree = self._build_cost_node_tree(cost_node_rows)

        return starter, cost_node_tree

    # =====================================================
    # BUILDERS
    # =====================================================

    def _build_contract_starter(
        self,
        row: dict[str, Any],
    ) -> ContractStarter:

        owner = self._company_eval.evaluate_from_tax(
            row["Owner NIP"],
            CompanyType.BUYER,
        )
        client = None
        if row["Client NIP"]:
            client = self._company_eval.evaluate_from_tax(
                row["Client NIP"],
                CompanyType.SELLER,
            )


        return ContractStarter(
            name=row["Name"],
            code=row["Code"],
            contract_owner=owner,
            client=client,
            description=row.get("Description"),
            start_date=row.get("Start Date"),
            end_date=row.get("End Date"),
            budget=(
                Decimal(str(row["Budget"]))
                if row.get("Budget") is not None
                else None
            ),
            path=Path(row["Path"]) if row.get("Path") is not None else None,
            status=ContractStatus[row["Status"]],
        )

    @staticmethod
    def _build_cost_node_tree(
            rows: list[dict[str, Any]],
    ) -> list[CostNodeInput]:
        """
        Build cost node tree from flat rows.

        Final, backward-compatible behavior:
        - if exactly ONE root → use it
        - if MORE THAN ONE root → create ONE technical root
        - Excel never needs to define a root explicitly
        - System always operates on a single tree
        """

        nodes: dict[str, CostNodeInput] = {}

        # =====================
        # CREATE NODES
        # =====================
        for row in rows:
            code = row["Code"]

            if code in nodes:
                raise ValueError(f"Duplicate cost node code '{code}'")

            nodes[code] = {
                "code": code,
                "name": row["Name"],
                "budget": (
                    Decimal(str(row["Budget"]))
                    if row.get("Budget") is not None
                    else None
                ),
                "quantity": (
                    Decimal(str(row["Quantity"]))
                    if row.get("Quantity") is not None
                    else None
                ),
                "unit": ApplyContractStructureExcelService._map_unit(
                    row.get("Unit")
                ),
                "children": [],
                "is_active": bool(row.get("Active", True)),
            }

        # =====================
        # BUILD RELATIONS
        # =====================
        roots: list[CostNodeInput] = []

        for row in rows:
            node = nodes[row["Code"]]
            parent_code = row.get("Parent Code")

            if parent_code:
                parent = nodes.get(parent_code)
                if not parent:
                    raise ValueError(
                        f"Parent code '{parent_code}' "
                        f"not found for node '{row['Code']}'"
                    )
                parent["children"].append(node)
            else:
                roots.append(node)

        # =====================
        # ENSURE SINGLE ROOT
        # =====================
        if len(roots) == 1:
            return roots

        # MULTIPLE ROOTS → create technical root
        technical_root: CostNodeInput = {
            "code": "ROOT",
            "name": "Contract root",
            "budget": None,
            "quantity": None,
            "unit": None,
            "children": roots,
            "is_active": True,
        }

        return [technical_root]

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _map_unit(value: Any) -> UnitOfMeasure | None:
        if value is None:
            return None
        try:
            return UnitOfMeasure(value)
        except ValueError:
            raise ValueError(f"Invalid unit '{value}'")
