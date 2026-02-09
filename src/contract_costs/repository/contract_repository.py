from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.contract import Contract


class ContractRepository(ABC):

    @abstractmethod
    def add(self, contract: Contract) -> None:
        """Persist new contract"""
        ...

    @abstractmethod
    def get(self, organization_id: UUID, contract_id: UUID) -> Contract | None:
        """Get contract by id (org scoped)"""
        ...

    @abstractmethod
    def list(self, organization_id: UUID) -> list[Contract]:
        """List all contracts for organization"""
        ...

    @abstractmethod
    def update(self, contract: Contract) -> None:
        """Update existing contract"""
        ...

    @abstractmethod
    def exists(self, organization_id: UUID, contract_id: UUID) -> bool:
        """Check if contract exists in organization"""
        ...

    @abstractmethod
    def get_by_code(
        self,
        organization_id: UUID,
        contract_code: str,
    ) -> Contract | None:
        """Get contract by code (org scoped)"""
        ...
