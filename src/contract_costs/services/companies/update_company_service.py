from dataclasses import replace
from datetime import datetime
from typing import Callable


from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_required_tax_number
from contract_costs.services.companies.dto.update_company_command import UpdateCompanyCommand


class UpdateCompanyService(ActionHandler[UpdateCompanyCommand,None]):

    def __init__(
        self,
        company_repository: CompanyRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._companies = company_repository
        self._clock = clock


    def execute(self, cmd: UpdateCompanyCommand) -> None:
        # Pobranie firmy W KONTEKŚCIE ORG
        company = self._companies.get(
            cmd.company_id,
            cmd.organization_id,
        )
        if company is None:
            raise ValueError("Company does not exist")

        # 2️⃣ Tax number
        if cmd.tax_number is None:
            normalized_tax = company.tax_number
        else:
            normalized_tax = normalize_required_tax_number(cmd.tax_number)

            existing = self._companies.get_by_tax_number(
                normalized_tax,
                cmd.organization_id,
            )
            if existing and existing.id != company.id:
                raise ValueError("Company with this tax number already exists")

        # 3️⃣ Budujemy nową wersję
        updated = replace(
            company,
            name=cmd.name,
            description=cmd.description,
            tax_number=normalized_tax,
            address=cmd.address,
            contact=cmd.contact,
            bank_account=cmd.bank_account,
            role=cmd.role,
            tags=cmd.tags or set(),
            updated_at=self._clock(),
            updated_by_user_id=cmd.actor_user_id,
        )

        # 4️⃣ Zapis
        self._companies.update(updated)
