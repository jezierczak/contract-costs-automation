from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.handler_registry import handles
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.company import Company, CompanyType
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_required_tax_number
from contract_costs.services.companies.dto.create_company_command import CreateCompanyCommand

@handles(CreateCompanyCommand)
class CreateCompanyService:

    def __init__(
        self,
        company_repository: CompanyRepository,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._companies = company_repository
        self._clock = clock
        self._id_generator = id_generator

    def execute(self, cmd: CreateCompanyCommand) -> Company:
        normalized_tax = normalize_required_tax_number(cmd.tax_number)

        # 1️⃣ uniqueness in org
        if self._companies.get_by_tax_number(
                normalized_tax,
                organization_id=cmd.organization_id,
        ):
            raise ValueError("Company with this tax number already exists in organization")

        # 2️⃣ OWN uniqueness
        if cmd.role == CompanyType.OWN:
            if self._companies.exists_owner(cmd.organization_id):
                raise ValueError("Organization already has OWN company")

        now = self._clock()

        company = Company(
            id=self._id_generator(),
            organization_id=cmd.organization_id,

            name=cmd.name,
            description=cmd.description,
            tax_number=normalized_tax,

            address=cmd.address,
            contact=cmd.contact,
            bank_account=cmd.bank_account,

            role=cmd.role,
            tags=cmd.tags or set(),
            is_active=True,

            created_at=now,
            created_by_user_id=cmd.actor_user_id,

            updated_at=None,
            updated_by_user_id=None,
        )

        self._companies.add(company)
        return company

