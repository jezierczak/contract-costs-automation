from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command
from contract_costs.model.unit_of_measure import UnitOfMeasure


@dataclass(frozen=True,slots=True)
@action_type(ActionType.CONTRACT_MANAGEMENT)
class UpdateContractNodeCommand(Command):
    contract_id: UUID
    node_id: UUID

    code: str
    name: str
    quantity: Decimal | None
    unit: UnitOfMeasure | None
    planned_budget: Decimal | None