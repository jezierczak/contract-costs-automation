from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.requires_role import requires_role
from contract_costs.model.company import CompanyType, Address, Contact, BankAccount
from contract_costs.model.identity.organization_role import OrganizationRole


@requires_role(
    OrganizationRole.OWNER,
          OrganizationRole.ADMIN,
          #OrganizationRole.USER
)
@dataclass(frozen=True)
class UpdateCompanyCommand:
    organization_id: UUID
    company_id: UUID
    actor_user_id: UUID

    name: str
    role: CompanyType
    address: Address
    contact: Contact | None
    description: str | None
    tax_number: str | None
    bank_account: BankAccount | None
    tags: set[str] | None
