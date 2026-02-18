from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command


@dataclass(frozen=True,slots=True)
class BaseApplyContractStructureExcelCommand(Command):
    excel_path: Path

@dataclass(frozen=True,slots=True)
@action_type(ActionType.CREATE_CONTRACT)
class ApplyNewContractStructureExcelCommand(BaseApplyContractStructureExcelCommand):
    ...

@dataclass(frozen=True,slots=True)
@action_type(ActionType.CONTRACT_MANAGEMENT)
class UpdateContractStructureExcelCommand(BaseApplyContractStructureExcelCommand):
    contract_id: UUID