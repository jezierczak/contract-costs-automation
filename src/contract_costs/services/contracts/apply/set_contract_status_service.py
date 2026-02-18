from dataclasses import replace
from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.model.contract import Contract
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.services.contracts.apply.command.set_contract_status_command import SetContractStatusCommand
from contract_costs.unit_of_work import UnitOfWork


class SetContractStatusService(ActionHandler[SetContractStatusCommand, None]):

    def __init__(
        self,
        # contract_repository: ContractRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        # self._contracts = contract_repository
        self._clock = clock

    def execute(self, *, action: SetContractStatusCommand, uow: UnitOfWork) -> None:
        contract_repo = uow.contracts

        contract = self._get_contract(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
            contract_repo=contract_repo
        )

        if contract.status == action.new_status:
            return

        updated = replace(
            contract,
            status=action.new_status,
            updated_at=self._clock(),
            updated_by_user_id=action.actor_user_id,
        )

        contract_repo.update(updated)

    @staticmethod
    def _get_contract( *, organization_id: UUID, contract_id: UUID,contract_repo:ContractRepository) -> Contract:
        contract = contract_repo.get(
            organization_id=organization_id,
            contract_id=contract_id,
        )
        if contract is None:
            raise ValueError("Contract does not exist")
        return contract
