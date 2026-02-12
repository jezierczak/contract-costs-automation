from uuid import UUID

from contract_costs.model.contract import Contract, ContractType
from contract_costs.repository.contract_repository import ContractRepository


class InMemoryContractRepository(ContractRepository):

    def __init__(self) -> None:
        self._contracts: dict[UUID, Contract] = {}

    # =========================================
    # CREATE
    # =========================================

    def add(self, contract: Contract) -> None:
        self._contracts[contract.id] = contract

    # =========================================
    # READ
    # =========================================

    def get(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
    ) -> Contract | None:
        contract = self._contracts.get(contract_id)
        if not contract:
            return None
        if contract.organization_id != organization_id:
            return None
        return contract

    def get_system_contract(
        self,
        *,
        organization_id: UUID,
        owner_id: UUID,
    ) -> Contract | None:
        for contract in self._contracts.values():
            if (
                contract.organization_id == organization_id
                and contract.owner.id == owner_id
                and contract.contract_type == ContractType.SYSTEM
            ):
                return contract
        return None

    def list_contracts(
        self,
        organization_id: UUID,
        contract_type: ContractType,
    ) -> list[Contract]:
        return [
            contract
            for contract in self._contracts.values()
            if contract.organization_id == organization_id
            and contract.contract_type == contract_type
        ]

    # =========================================
    # UPDATE
    # =========================================

    def update(self, contract: Contract) -> None:
        self._contracts[contract.id] = contract

    # =========================================
    # EXISTS
    # =========================================

    def exists(
        self,
        organization_id: UUID,
        contract_id: UUID,
    ) -> bool:
        contract = self._contracts.get(contract_id)
        return (
            contract is not None
            and contract.organization_id == organization_id
        )

    # =========================================
    # LOOKUP BY CODE
    # =========================================

    def get_by_code(
        self,
        organization_id: UUID,
        contract_code: str,
    ) -> Contract | None:
        for contract in self._contracts.values():
            if (
                contract.organization_id == organization_id
                and contract.code == contract_code
            ):
                return contract
        return None
