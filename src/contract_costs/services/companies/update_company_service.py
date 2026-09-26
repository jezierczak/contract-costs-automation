from dataclasses import replace
from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_required_tax_number
from contract_costs.services.companies.dto.update_company_command import BaseUpdateCompanyCommand
from contract_costs.unit_of_work import UnitOfWork


class UpdateCompanyService(ActionHandler[BaseUpdateCompanyCommand, None]):

    def __init__(
        self,
        # company_repository: CompanyRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        # self._companies = company_repository
        self._clock = clock

    def execute(self, *, action: BaseUpdateCompanyCommand, uow: UnitOfWork) -> None:
        repo = uow.companies
        company = repo.get(
            action.company_id,
            action.organization_id,
        )
        # company = self._companies.get(
        #     action.company_id,
        #     action.organization_id,
        # )
        if company is None:
            raise ValueError("Company does not exist")

        if action.tax_number is None:
            normalized_tax = company.tax_number
        else:
            normalized_tax = normalize_required_tax_number(action.tax_number)

            existing = repo.get_by_tax_number(
                normalized_tax,
                action.organization_id,
            )
            if existing and existing.id != company.id:
                raise ValueError("Company with this tax number already exists")

        updated = replace(
            company,
            name=action.name,
            description=action.description,
            tax_number=normalized_tax,
            address=action.address,
            contact=action.contact,
            bank_account=action.bank_account,
            role=action.role,
            tags=action.tags or set(),
            reference_numbering_mode=(
                action.reference_numbering_mode
                if action.set_reference_numbering_mode
                else company.reference_numbering_mode
            ),
            updated_at=self._clock(),
            updated_by_user_id=action.actor_user_id,
        )

        repo.update(updated)
