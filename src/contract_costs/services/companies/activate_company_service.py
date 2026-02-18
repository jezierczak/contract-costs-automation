from dataclasses import replace
from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.companies.dto.activate_company_command import (
    BaseActivateCompanyCommand,
)
from contract_costs.unit_of_work import UnitOfWork


class ActivateCompanyService(ActionHandler[BaseActivateCompanyCommand,None]):

    def __init__(
        self,
        # company_repository: CompanyRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        # self._companies = company_repository
        self._clock = clock

    def execute(self, *, action: BaseActivateCompanyCommand, uow: UnitOfWork) -> None:
        repo = uow.companies
        company = repo.get(
            action.company_id,
            action.organization_id,
        )
        if company is None:
            raise ValueError("Company does not exist")

        if company.is_active:
            return  # idempotent

        updated = replace(
            company,
            is_active=True,
            updated_at=self._clock(),
            updated_by_user_id=action.actor_user_id,
        )

        repo.update(updated)
