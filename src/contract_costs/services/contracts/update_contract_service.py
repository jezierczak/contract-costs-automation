from dataclasses import replace
from datetime import date
from uuid import UUID

from contract_costs.model.contract import Contract, ContractStatus
from contract_costs.repository.contract_repository import ContractRepository


class UpdateContractService:

    def __init__(self, contract_repository: ContractRepository) -> None:
        self._contract_repository = contract_repository

    def update_metadata(
        self,
        contract_id: UUID,
        *,
        name: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> None:
        contract = self._get_contract(contract_id)

        updated = replace(
            contract,
            name=name if name is not None else contract.name,
            start_date=start_date if start_date is not None else contract.start_date,
            end_date=end_date if end_date is not None else contract.end_date,
        )

        self._contract_repository.update(updated)

    def change_status(self, contract_id: UUID, status: ContractStatus) -> None:
        contract = self._get_contract(contract_id)
        updated = replace(contract, status=status)
        self._contract_repository.update(updated)


    def _get_contract(self, contract_id: UUID) -> Contract:
        contract = self._contract_repository.get(contract_id)
        if contract is None:
            raise ValueError("Contract does not exist")
        return contract
