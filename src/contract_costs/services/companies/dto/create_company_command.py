from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.model.company import CompanyType, Address, Contact, BankAccount



@action_type(ActionType.CREATE_COMPANY)
@dataclass(frozen=True)
class CreateCompanyCommand(Action):
    # organization_id: UUID
    # actor_user_id: UUID | None

    name: str
    tax_number: str
    role: CompanyType

    description: str | None = None
    address: Address | None = None
    contact: Contact | None = None
    bank_account: BankAccount | None = None
    tags: set[str] | None = None
