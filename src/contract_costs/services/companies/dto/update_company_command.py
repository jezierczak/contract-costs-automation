from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command
# from contract_costs.action_bus.requires_role import requires_role
from contract_costs.model.company import CompanyType, Address, Contact, BankAccount
# from contract_costs.model.identity.organization_role import OrganizationRole


@action_type(ActionType.COMPANY_MANAGEMENT)
@dataclass(frozen=True)
class UpdateCompanyCommand(Command):
    company_id: UUID
    name: str
    role: CompanyType
    address: Address
    contact: Contact | None
    description: str | None
    tax_number: str | None
    bank_account: BankAccount | None
    tags: set[str] | None
