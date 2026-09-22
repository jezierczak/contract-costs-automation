from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.company import Company, CompanyType

from contract_costs.services.common.resolve_utils import normalize_required_tax_number
from contract_costs.services.companies.dto.create_company_command import BaseCreateCompanyCommand
from contract_costs.services.contracts.system_contract.create_system_contract_orchestrator import (
    CreateSystemContractOrchestrator,
)
from contract_costs.unit_of_work import UnitOfWork


class CreateCompanyService(ActionHandler[BaseCreateCompanyCommand, Company]):

    def __init__(
        self,
        # company_repository: CompanyRepository,
        create_system_contract: CreateSystemContractOrchestrator,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        # self._companies = company_repository
        self._create_system_contract = create_system_contract
        self._clock = clock
        self._id_generator = id_generator

    def execute(self, *, action: BaseCreateCompanyCommand, uow: UnitOfWork) -> Company:
        normalized_tax = normalize_required_tax_number(action.tax_number)
        repo = uow.companies
        if repo.get_by_tax_number(
            normalized_tax,
            organization_id=action.organization_id,
        ):
            raise ValueError("Company with this tax number already exists in organization")

        now = self._clock()

        company = Company(
            id=self._id_generator(),
            organization_id=action.organization_id,
            name=action.name,
            description=action.description,
            tax_number=normalized_tax,
            address=action.address,
            contact=action.contact,
            bank_account=action.bank_account,
            role=action.role,
            tags=action.tags or set(),
            is_active=True,
            created_at=now,
            created_by_user_id=action.actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
        )

        repo.add(company)

        if company.role == CompanyType.OWN:
            self._create_system_contract.execute(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                owner=company,
                uow=uow
            )

        return company
