from dataclasses import dataclass
from datetime import date
from uuid import UUID

from contract_costs.action_bus.action import Action


@dataclass(frozen=True)
class ContractDetailsQuery(Action):
    contract_id: UUID
    at_date: date | None = None
