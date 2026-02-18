from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action import Action

@dataclass(frozen=True,slots=True)
class Command(Action):
   organization_id: UUID
   actor_user_id: UUID
