from dataclasses import replace
from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.common.time import utc_now
from contract_costs.model.contract import Contract
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.services.contracts.apply.command.set_contract_status_command import (
    SetContractStatusCommand
)

class SetContractStatusService:

    def __init__(
        self,
        contract_repository: ContractRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._contracts = contract_repository
        self._clock = clock

    def execute(self, command: SetContractStatusCommand) -> None:
        contract = self._get_contract(
            organization_id=command.organization_id,
            contract_id=command.contract_id,
        )

        if contract.status == command.new_status:
            return  # idempotent

        updated = replace(
            contract,
            status=command.new_status,
            updated_at=self._clock(),
            updated_by_user_id=command.actor_user_id,
        )

        self._contracts.update(updated)

    def _get_contract(
            self,
            *,
            organization_id: UUID,
            contract_id: UUID,
    ) -> Contract:
        contract = self._contracts.get(
            organization_id=organization_id,
            contract_id=contract_id,
        )
        if contract is None:
            raise ValueError("Contract does not exist")
        return contract
