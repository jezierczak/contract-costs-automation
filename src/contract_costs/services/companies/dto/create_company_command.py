from dataclasses import dataclass

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command
from contract_costs.model.company import CompanyType, Address, Contact, BankAccount



@action_type(ActionType.COMPANY_MANAGEMENT)
@dataclass(frozen=True)
class CreateCompanyCommand(Command):

    name: str
    tax_number: str
    role: CompanyType

    description: str | None = None
    address: Address | None = None
    contact: Contact | None = None
    bank_account: BankAccount | None = None
    tags: set[str] | None = None
