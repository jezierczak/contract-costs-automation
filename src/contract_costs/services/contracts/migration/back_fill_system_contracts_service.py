from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.contracts.migration.backfill_system_contracts_command import BackfillSystemContractsCommand
from contract_costs.services.contracts.system_contract.create_system_contract_orchestrator import \
    CreateSystemContractOrchestrator
from contract_costs.unit_of_work import UnitOfWork


class BackfillSystemContractsService(
    ActionHandler[BackfillSystemContractsCommand, None]
):

    def __init__(
        self,
        # company_repository: CompanyRepository,
        create_system_contract: CreateSystemContractOrchestrator,
    ) -> None:
        # self._companies = company_repository
        self._create_system = create_system_contract

    def execute(
        self,
        *,
        action: BackfillSystemContractsCommand,
        uow: UnitOfWork,

    ) -> None:

        owners = uow.companies.get_owners(
            organization_id=action.organization_id
        )

        for owner in owners:
            self._create_system.execute(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                owner=owner,
                uow=uow,
            )
