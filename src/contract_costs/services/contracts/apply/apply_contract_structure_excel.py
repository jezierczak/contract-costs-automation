import logging
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import contract_costs.config as cfg
from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.infrastructure.excel.contracts.contract_prepare_columns import CONTRACT_PREPARE_COLUMNS
from contract_costs.infrastructure.excel.contracts.cost_node_prepare_columns import CONTRACT_NODE_PREPARE_COLUMNS
from contract_costs.infrastructure.excel.excel_loader import ExcelLoader
from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractStatus, ContractType
from contract_costs.model.contract_node import ContractNodeInput
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.contracts.apply.command.apply_contract_structure_excel_command import \
    BaseApplyContractStructureExcelCommand, ApplyNewContractStructureExcelCommand, UpdateContractStructureExcelCommand
from contract_costs.services.contracts.apply.command.update_contract_structure_command import UpdateContractStructureCommand
from contract_costs.services.contracts.apply.dto.contract_excel_data import ContractExcelData
from contract_costs.services.contracts.apply.update_contract_structure_service import UpdateContractStructureService
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ApplyContractStructureExcelService(ActionHandler[BaseApplyContractStructureExcelCommand,None]):
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

    def execute(
        self,
        *,
        action: BaseApplyContractStructureExcelCommand,
        uow: UnitOfWork,
    ) -> None:

        excel_data, nodes = self._load_from_excel(
            path=action.excel_path,
            organization_id=action.organization_id,
            actor_user_id=action.actor_user_id,
            uow=uow,
        )

        if isinstance(action, ApplyNewContractStructureExcelCommand):
            self._handle_create(
                base_action=action,
                excel_data=excel_data,
                nodes=nodes,
                uow=uow
            )

        elif isinstance(action, UpdateContractStructureExcelCommand):
            self._handle_update(
                base_action=action,
                excel_data=excel_data,
                nodes=nodes,
                uow=uow
            )


        else:
            logger.error("Unsupported command type: %s", type(action))
            raise RuntimeError("Unsupported command type")

    def _handle_create(
        self,
        *,
        base_action: ApplyNewContractStructureExcelCommand,
        excel_data: ContractExcelData,
        nodes: list[ContractNodeInput],
        uow: UnitOfWork,
    ) -> None:

        action = CreateContractCommand(
            organization_id=base_action.organization_id,
            actor_user_id=base_action.actor_user_id,
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
            contract_type=ContractType.PROJECT,
            contract_node_input=nodes,
        )

        self._create_contract.execute(action=action, uow=uow)

    def _handle_update(
        self,
        *,
        base_action: UpdateContractStructureExcelCommand,
        excel_data: ContractExcelData,
        nodes: list[ContractNodeInput],
        uow: UnitOfWork,
    ) -> None:


        action = UpdateContractStructureCommand(
            organization_id=base_action.organization_id,
            actor_user_id=base_action.actor_user_id,
            contract_id=base_action.contract_id,
            name=excel_data.name,
            description=excel_data.description,
            start_date=excel_data.start_date,
            end_date=excel_data.end_date,
            budget=excel_data.budget,
            status=excel_data.status,
            path=excel_data.path,
            contract_node_input=nodes,
        )

        self._update_contract.execute(action=action, uow=uow)

    def _load_from_excel(
        self,
        *,
        uow: UnitOfWork,
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
            raise ValueError("Contract sheet must contain exactly one row")

        contract_node_rows = ExcelLoader.load(
            input_path=path,
            sheet_name=self.CONTRACT_NODES_SHEET,
            columns=CONTRACT_NODE_PREPARE_COLUMNS,
        )

        contract_excel_data = self._build_contract_excel_data(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            row=contract_rows[0],
            uow=uow
        )
        contract_node_tree = self._build_contract_node_tree(contract_node_rows)

        return contract_excel_data, contract_node_tree

    def _build_contract_excel_data(
        self,
        *,
        uow:UnitOfWork,
        organization_id: UUID,
        actor_user_id: UUID,
        row: dict[str, Any],
    ) -> ContractExcelData:
        owner = self._company_eval.evaluate_from_tax(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            input_tax_number=row["Owner NIP"],
            role=CompanyType.BUYER,
            uow=uow
        )

        client = None
        if row["Client NIP"]:
            client = self._company_eval.evaluate_from_tax(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                input_tax_number=row["Client NIP"],
                role=CompanyType.SELLER,
                uow=uow
            )

        return ContractExcelData(
            name=row["Name"],
            code=row["Code"],
            description=row.get("Description"),
            owner=owner,
            client=client,
            start_date=row.get("Start Date"),
            end_date=row.get("End Date"),
            budget=(Decimal(str(row["Budget"])) if row.get("Budget") is not None else None),
            path=Path(row["Path"]) if row.get("Path") else None,
            status=ContractStatus[row["Status"]],
        )

    @staticmethod
    def _build_contract_node_tree(rows: list[dict[str, Any]]) -> list[ContractNodeInput]:
        nodes: dict[str, ContractNodeInput] = {}

        for row in rows:
            code = row["Code"]
            if code in nodes:
                raise ValueError(f"Duplicate cost node code '{code}'")

            nodes[code] = {
                "code": code,
                "name": row["Name"],
                "budget": Decimal(str(row["Budget"])) if row.get("Budget") is not None else None,
                "quantity": Decimal(str(row["Quantity"])) if row.get("Quantity") is not None else None,
                "unit": ApplyContractStructureExcelService._map_unit(row.get("Unit")),
                "children": [],
                "is_active": bool(row.get("Active", True)),
            }

        roots: list[ContractNodeInput] = []

        for row in rows:
            node = nodes[row["Code"]]
            parent_code = row.get("Parent Code")

            if parent_code:
                parent = nodes.get(parent_code)
                if not parent:
                    raise ValueError(f"Parent code '{parent_code}' not found for node '{row['Code']}'")
                parent["children"].append(node)
            else:
                roots.append(node)

        if len(roots) == 1:
            return roots

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

    @staticmethod
    def _map_unit(value: Any) -> UnitOfMeasure | None:
        if value is None:
            return None
        try:
            return UnitOfMeasure(value)
        except ValueError as exc:
            raise ValueError(f"Invalid unit '{value}'") from exc
