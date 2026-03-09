from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.command import Command
from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.model.company import Company


@action_type(ActionType.CONTRACT_MANAGEMENT)
@dataclass(frozen=True, slots=True)
class UpdateContractCommand(Command):

    contract_id: UUID

    code: str
    name: str
    description: str | None

    owner: Company | None
    client: Company | None