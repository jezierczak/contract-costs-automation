from uuid import UUID

from contract_costs.model.contract import Contract, ContractType, ContractStatus
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

    def list_all_by_type(
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

    def list_contracts(
            self,
            *,
            organization_id: UUID,
            contract_type: ContractType | None = None,
            status: ContractStatus | None = None,
            search: str | None = None,
    ) -> list[Contract]:

        result: list[Contract] = []

        for contract in self._contracts.values():

            # --- organization filter ---
            if contract.organization_id != organization_id:
                continue

            # --- contract type filter ---
            if contract_type is not None and contract.contract_type != contract_type:
                continue

            # --- status filter ---
            if status is not None and contract.status != status:
                continue

            # --- search filter (code + name) ---
            if search:
                s = search.lower()
                if s not in contract.code.lower() and s not in contract.name.lower():
                    continue

            result.append(contract)

        # takie samo zachowanie jak SQL (ORDER BY created_at DESC)
        result.sort(key=lambda c: c.created_at, reverse=True)

        return result

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
