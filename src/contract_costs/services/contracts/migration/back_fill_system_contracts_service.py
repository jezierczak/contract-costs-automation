from uuid import UUID

from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.contracts.system_contract.create_system_contract_orchestrator import \
    CreateSystemContractOrchestrator


class BackfillSystemContractsService:

    def __init__(
        self,
        company_repository: CompanyRepository,
        create_system_contract: CreateSystemContractOrchestrator,
    ) -> None:
        self._companies = company_repository
        self._create_system = create_system_contract

    def execute(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
    ) -> None:

        owners = self._companies.get_owners(
            organization_id=organization_id
        )

        for owner in owners:
            self._create_system.execute(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                owner=owner,
            )
