import logging
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
    CONTRACT_NODE_PREPARE_COLUMNS,
)

from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractStatus
from contract_costs.model.contract_node import ContractNodeInput
from contract_costs.model.unit_of_measure import UnitOfMeasure

from contract_costs.services.companies.company_evaluate_orchestrator import (
    CompanyEvaluateOrchestrator,
)
from contract_costs.services.contracts.apply.command.update_contract_structure_command import \
    UpdateContractStructureCommand
from contract_costs.services.contracts.apply.dto.contract_excel_data import ContractExcelData
from contract_costs.services.contracts.create_contract_service import (
    CreateContractService,
)
from contract_costs.services.contracts.apply.update_contract_structure_service import (
    UpdateContractStructureService,
)
from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand

logger = logging.getLogger(__name__)

class ApplyContractStructureExcelService:
    """
    Orchestrator:
    - NEW contract (create)
    - EDIT existing contract (replace structure)

    Excel is the source of truth.
    """

    CONTRACT_SHEET = cfg.CONTRACT_METADATA_SHEET_NAME
    CONTRACT_NODES_SHEET = cfg.CONTRACT_ITEMS_SHEET_NAME


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

    def apply_new(self,
                  *,
                  excel_path: Path,
                  organization_id: UUID,
                  actor_user_id: UUID
                  ) -> None:

        excel_data, contract_nodes = self._load_from_excel(excel_path,organization_id,actor_user_id)

        command = CreateContractCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            code=excel_data.code,
            name=excel_data.name,
            description=excel_data.description,
            owner=excel_data.owner,
            client=excel_data.client,
            start_date=excel_data.start_date,
            end_date=excel_data.end_date,
            budget=excel_data.budget,
            path=excel_data.path,
            status=excel_data.status,
        )

        self._create_contract.init(command=command)
        self._create_contract.add_contract_node_tree(contract_nodes)
        self._create_contract.execute()

    def apply_update(self,
                     *,
                     excel_path: Path,
                     contract_id: UUID,
                     organization_id: UUID,
                     actor_user_id: UUID
                     ) -> None:
        excel_data, contract_nodes = self._load_from_excel(excel_path,organization_id,actor_user_id)

        command = UpdateContractStructureCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            contract_id=contract_id,
            name=excel_data.name,
            description=excel_data.description,
            start_date=excel_data.start_date,
            end_date=excel_data.end_date,
            budget=excel_data.budget,
            status=excel_data.status,
            path=excel_data.path,
            contract_node_input=contract_nodes,
        )

        self._update_contract.execute(
            command
        )

    # =====================================================
    # LOADING
    # =====================================================

    def _load_from_excel(
            self,
            path: Path,
            organization_id: UUID,
            actor_user_id: UUID,
    ) -> tuple[ContractExcelData, list[ContractNodeInput]]:

        contract_rows = ExcelLoader.load(
            input_path=path,
            sheet_name=self.CONTRACT_SHEET,
            columns=CONTRACT_PREPARE_COLUMNS,
        )
        logger.debug("Loaded contract rows: %s", contract_rows)
        if len(contract_rows) != 1:
            raise ValueError(
                "Contract sheet must contain exactly one row"
            )

        contract_node_rows = ExcelLoader.load(
            input_path=path,
            sheet_name=self.CONTRACT_NODES_SHEET,
            columns=CONTRACT_NODE_PREPARE_COLUMNS,
        )

        contract_excel_data = self._build_contract_excel_data(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            row=contract_rows[0],
        )
        contract_node_tree = self._build_contract_node_tree(contract_node_rows)

        return contract_excel_data, contract_node_tree

    # =====================================================
    # BUILDERS
    # =====================================================

    def _build_contract_excel_data(
            self,
            *,
            organization_id:UUID,
            actor_user_id:UUID,
            row: dict[str, Any],
    ) -> ContractExcelData:

        owner = self._company_eval.evaluate_from_tax(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            input_tax_number=row["Owner NIP"],
            role=CompanyType.BUYER,
        )

        client = None
        if row["Client NIP"]:
            client = self._company_eval.evaluate_from_tax(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                input_tax_number=row["Client NIP"],
                role=CompanyType.SELLER,
            )

        return ContractExcelData(
            name=row["Name"],
            code=row["Code"],
            description=row.get("Description"),
            owner=owner,
            client=client,
            start_date=row.get("Start Date"),
            end_date=row.get("End Date"),
            budget=(
                Decimal(str(row["Budget"]))
                if row.get("Budget") is not None
                else None
            ),
            path=Path(row["Path"]) if row.get("Path") else None,
            status=ContractStatus[row["Status"]],
        )

    @staticmethod
    def _build_contract_node_tree(
            rows: list[dict[str, Any]],
    ) -> list[ContractNodeInput]:
        """
        Build contract node tree from flat rows.

        Final, backward-compatible behavior:
        - if exactly ONE root → use it
        - if MORE THAN ONE root → create ONE technical root
        - Excel never needs to define a root explicitly
        - System always operates on a single tree
        """

        nodes: dict[str, ContractNodeInput] = {}

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
        roots: list[ContractNodeInput] = []

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
        technical_root: ContractNodeInput = {
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
