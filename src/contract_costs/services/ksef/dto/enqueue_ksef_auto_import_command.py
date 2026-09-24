from dataclasses import dataclass

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command


@action_type(ActionType.UPLOAD_DOCUMENT)
@dataclass(frozen=True)
class EnqueueKsefAutoImportCommand(Command):
    # True = pomiń firmy, które dziś miały już udany import (nadrabianie po starcie)
    skip_imported_today: bool = False
