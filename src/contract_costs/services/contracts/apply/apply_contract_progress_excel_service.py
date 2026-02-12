from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID
from datetime import date


from contract_costs.infrastructure.excel.contracts.contract_node_progress_prepare_columns import \
    CONTRACT_NODE_PROGRESS_PREPARE_COLUMNS
from contract_costs.infrastructure.excel.excel_loader import ExcelLoader
from contract_costs.model.contract import Contract

import contract_costs.config as cfg
from contract_costs.services.contracts.apply.apply_contract_progress_service import ApplyContractProgressService
from contract_costs.services.contracts.apply.command.apply_contract_progerss_command import \
    ApplyContractProgressCommand, ContractNodeProgressUpdate



class ApplyContractProgressExcelService:
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

    def apply(
            self,
            *,
            contract: Contract,
            excel_path: Path,
            organization_id: UUID,
            actor_user_id: UUID,
    ) -> None:
        rows = self._load_from_excel(excel_path)

        self._apply_progress_rows(
            contract=contract,
            rows=rows,
            organization_id=organization_id,
            actor_user_id=actor_user_id
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
            organization_id: UUID,
            actor_user_id: UUID,
            contract: Contract,
            rows: list[dict[str, Any]],
    ) -> None:

        updates: list[ContractNodeProgressUpdate] = []
        today = date.today()

        for row in rows:
            if row["Contract"] != contract.code:
                raise ValueError(...)

            node_id = UUID(row["Node ID"])
            new_progress = row.get("New Progress [%]")

            if new_progress is None:
                continue

            if not (Decimal("0") <= new_progress <= Decimal("100")):
                raise ValueError(...)

            updates.append(
                ContractNodeProgressUpdate(
                    contract_node_id=node_id,
                    progress=Decimal(new_progress) / Decimal("100"),
                    progress_date=today,
                )
            )

        if not updates:
            return  # optional, żeby nie odpalać pustego command

        command = ApplyContractProgressCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            contract_id=contract.id,
            updates=updates,
        )

        self._apply_contract_progress_service.execute(command)

        # nodes = self._node_repo.list_by_contract(organization_id=organization_id,contract_id=contract.id)
        # tree = ContractNodeTreeIndex(nodes)
        # nodes_by_id = {n.id: n for n in nodes}
        #
        # today = date.today()  # albo data z nagłówka Excela później
        #
        # for row in rows:
        #     # --- contract safety ---
        #     if row["Contract"] != contract.code:
        #         raise ValueError(
        #             f"Row contract '{row['Contract']}' "
        #             f"does not match '{contract.code}'"
        #         )
        #
        #     node_id = UUID(row["Node ID"])
        #     new_progress = row.get("New Progress [%]")
        #
        #     # --- skip empty ---
        #     if new_progress is None:
        #         continue
        #
        #     if not (Decimal("0") <= new_progress <= Decimal("100")):
        #         raise ValueError(
        #             f"Invalid progress {new_progress} for node {row['Code']}"
        #         )
        #
        #     node = nodes_by_id.get(node_id)
        #     if not node:
        #         raise ValueError(f"Contract node {node_id} not found")
        #
        #     if node.contract_id != contract.id:
        #         raise ValueError(
        #             f"Node {node.code} does not belong to contract {contract.code}"
        #         )
        #
        #     # --- leaf only ---
        #     if not tree.is_leaf(node):
        #         raise ValueError(
        #             f"Progress can be set only on leaf nodes ({node.code})"
        #         )
        #
        #     if not node.is_active:
        #         continue  # albo raise – decyzja domenowa
        #     progress = ContractNodeProgress(
        #         organization_id=organization_id,
        #         created_at=self._clock(),
        #         created_by_user_id = actor_user_id,
        #         updated_at=None,
        #         updated_by_user_id = None,
        #         id= self._id_generator(),
        #         contract_node_id=node.id,
        #         progress=new_progress / Decimal("100"),
        #         progress_date=today
        #     )
        #     # ✅ JEDYNA POPRAWNA OPERACJA
        #     self._node_repo.add_progress(
        #         progress=progress,
        #     )
