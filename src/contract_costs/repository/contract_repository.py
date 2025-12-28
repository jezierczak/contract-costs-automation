from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.contract import Contract


class ContractRepository(ABC):

    @abstractmethod
    def add(self, contract: Contract) -> None:
        """Persist new contract"""
        ...

    @abstractmethod
    def get(self, contract_id: UUID) -> Contract | None:
        """Get contract by id"""
        ...

    @abstractmethod
    def list(self) -> list[Contract]:
        """List all contracts"""
        ...

    @abstractmethod
    def update(self, contract: Contract) -> None:
        """Update existing contract"""
        ...

    @abstractmethod
    def exists(self, contract_id: UUID) -> bool:
        """Check if contract exists"""
        ...
    @abstractmethod
    def get_by_code(self, contract_code: str) -> Contract | None:
        ...