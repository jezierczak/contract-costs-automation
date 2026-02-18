from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command


@dataclass(frozen=True,slots=True)
@action_type(ActionType.CREATE_SNAPSHOT)
class CreateContractSnapshotCommand(Command):

    contract_id: UUID
    snapshot_date: date
