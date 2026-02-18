from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command


@dataclass(frozen=True,slots=True)
@action_type(ActionType.CONTRACT_PROGRESS_MANAGEMENT)
class ApplyContractProgressExcelCommand(Command):
    contract_id: UUID
    # contract_code: str  # ← dodaj to jeśli chcesz walidować excel
    excel_path: Path