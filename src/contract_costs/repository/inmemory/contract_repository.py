from uuid import UUID

from contract_costs.model.contract import Contract
from contract_costs.repository.contract_repository import ContractRepository


class InMemoryContractRepository(ContractRepository):
    def __init__(self) -> None:
        self._contracts: dict[UUID, Contract] = {}

    def add(self, contract: Contract) -> None:
        self._contracts[contract.id] = contract

    def get(self, contract_id: UUID) -> Contract | None:
        return self._contracts.get(contract_id)

    def list(self) -> list[Contract]:
        return list(self._contracts.values())

    def update(self, contract: Contract) -> None:
        self._contracts[contract.id] = contract

    def exists(self, contract_id: UUID) -> bool:
        return contract_id in self._contracts