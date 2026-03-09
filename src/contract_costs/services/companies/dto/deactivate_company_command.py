from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import action_type, ActionType


@dataclass(frozen=True,slots=True)
class BaseDeactivateCompanyCommand(Action):
    organization_id: UUID
    company_id: UUID
    actor_user_id: UUID


@action_type(ActionType.OWNER_COMPANY_MANAGEMENT)
@dataclass(frozen=True,slots=True)
class DeactivateOwnerCompanyCommand(BaseDeactivateCompanyCommand):
    pass


@action_type(ActionType.COUNTERPARTY_MANAGEMENT)
@dataclass(frozen=True,slots=True)
class DeactivateCounterpartyCompanyCommand(BaseDeactivateCompanyCommand):
    pass