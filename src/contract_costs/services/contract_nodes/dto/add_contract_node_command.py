from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command
from contract_costs.model.unit_of_measure import UnitOfMeasure


@action_type(ActionType.CONTRACT_MANAGEMENT)
@dataclass(frozen=True,slots=True)
class AddContractNodeCommand(Command):
    contract_id: UUID
    parent_id: UUID | None
    code:str
    name: str
    quantity:Decimal | None
    unit:UnitOfMeasure
    planned_budget: Decimal | None