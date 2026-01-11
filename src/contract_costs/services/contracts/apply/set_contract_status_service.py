from dataclasses import replace
from uuid import UUID

from contract_costs.model.contract import Contract
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.services.contracts.apply.command.set_contract_status_command import (
    SetContractStatusCommand
)

class SetContractStatusService:

    def __init__(self, contract_repository: ContractRepository) -> None:
        self._contracts = contract_repository

    def execute(self, command: SetContractStatusCommand) -> None:
        contract = self._get_contract(command.contract_id)

        if contract.status == command.new_status:
            return  # idempotent

        updated = replace(
            contract,
            status=command.new_status,
        )

        self._contracts.update(updated)

    def _get_contract(self, contract_id: UUID) -> Contract:
        contract = self._contracts.get(contract_id)
        if contract is None:
            raise ValueError("Contract does not exist")
        return contract
