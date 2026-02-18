from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType


@dataclass(frozen=True)
class BaseDeactivateCompanyCommand:
    organization_id: UUID
    company_id: UUID
    actor_user_id: UUID


@action_type(ActionType.OWNER_COMPANY_MANAGEMENT)
@dataclass(frozen=True)
class DeactivateOwnerCompanyCommand(BaseDeactivateCompanyCommand):
    pass


@action_type(ActionType.COUNTERPARTY_MANAGEMENT)
@dataclass(frozen=True)
class DeactivateCounterpartyCompanyCommand(BaseDeactivateCompanyCommand):
    pass