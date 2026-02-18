from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID
from datetime import date

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.infrastructure.excel.contracts.contract_node_progress_prepare_columns import \
    CONTRACT_NODE_PROGRESS_PREPARE_COLUMNS
from contract_costs.infrastructure.excel.excel_loader import ExcelLoader

import contract_costs.config as cfg
from contract_costs.services.contracts.apply.apply_contract_progress_service import ApplyContractProgressService
from contract_costs.services.contracts.apply.command.apply_contract_progerss_command import \
    ApplyContractProgressCommand, ContractNodeProgressUpdate
from contract_costs.services.contracts.apply.command.apply_contract_progress_excel_command import \
    ApplyContractProgressExcelCommand
from contract_costs.unit_of_work import UnitOfWork


class ApplyContractProgressExcelService(
    ActionHandler[ApplyContractProgressExcelCommand, None]
):
    """
    Orchestrator:
    - applies progress updates to existing contract nodes
    - Excel is the source of truth for progress values
    """

    CONTRACT_PROGRESS_SHEET = cfg.CONTRACT_ITEMS_SHEET_NAME

    def __init__(
        self,
        # contract_node_repository: ContractNodeRepository,
        apply_contract_progress_service: ApplyContractProgressService,
        # id_generator: Callable[[], UUID] = new_uuid,
        # clock: Callable[[], datetime] = utc_now,
    ) -> None:
        # self._node_repo = contract_node_repository
        self._apply_contract_progress_service = apply_contract_progress_service
        # self._id_generator = id_generator
        # self._clock = clock

    def execute(self, *, action: ApplyContractProgressExcelCommand, uow: UnitOfWork) -> None:

        rows = self._load_from_excel(action.excel_path)

        updates = self._build_updates(rows)

        if not updates:
            return

        command = ApplyContractProgressCommand(
            organization_id=action.organization_id,
            actor_user_id=action.actor_user_id,
            contract_id=action.contract_id,
            updates=updates,
        )

        self._apply_contract_progress_service.execute(
            action=command,
            uow=uow
        )

    # -----------------------------------------
    # Excel parsing
    # -----------------------------------------
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

        # -----------------------------------------
        # Build domain updates
        # -----------------------------------------

    @staticmethod
    def _build_updates(
            rows: list[dict[str, Any]],
    ) -> list[ContractNodeProgressUpdate]:

        updates: list[ContractNodeProgressUpdate] = []
        today = date.today()

        for row in rows:

            node_id = UUID(row["Node ID"])
            new_progress = row.get("New Progress [%]")

            if new_progress is None:
                continue

            if not (Decimal("0") <= new_progress <= Decimal("100")):
                raise ValueError(
                    f"Invalid progress value {new_progress} for node {node_id}"
                )

            updates.append(
                ContractNodeProgressUpdate(
                    contract_node_id=node_id,
                    progress=Decimal(new_progress) / Decimal("100"),
                    progress_date=today,
                )
            )

        return updates
