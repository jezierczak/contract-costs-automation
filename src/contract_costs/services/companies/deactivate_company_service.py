from dataclasses import replace
from datetime import datetime
from typing import Callable

from contract_costs.common.time import utc_now
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.companies.dto.deactivate_company_command import (
    DeactivateCompanyCommand,
)


class DeactivateCompanyService:

    def __init__(
        self,
        company_repository: CompanyRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._companies = company_repository
        self._clock = clock

    def execute(self, cmd: DeactivateCompanyCommand) -> None:
        company = self._companies.get(
            cmd.company_id,
            cmd.organization_id,
        )
        if company is None:
            raise ValueError("Company does not exist")

        if not company.is_active:
            return  # idempotent

        updated = replace(
            company,
            is_active=False,
            updated_at=self._clock(),
            updated_by_user_id=cmd.actor_user_id,
        )

        self._companies.update(updated)
