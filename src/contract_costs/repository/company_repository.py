from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.company import Company


class CompanyRepository(ABC):

    @abstractmethod
    def add(self, company: Company) -> None:
        ...

    @abstractmethod
    def get(self, company_id: UUID) -> Company | None:
        ...

    @abstractmethod
    def list(self) -> list[Company]:
        ...

    @abstractmethod
    def update(self, company: Company) -> None:
        ...

    @abstractmethod
    def exists(self, company_id: UUID) -> bool:
        ...
