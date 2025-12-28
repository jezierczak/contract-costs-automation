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
    def list_all(self) -> list[Company]:
        ...

    @abstractmethod
    def get_by_tax_number(self, tax_number: str) -> Company | None:
        ...

    @abstractmethod
    def get_owners(self) -> list[Company]:
        ...

    @abstractmethod
    def update(self, company: Company) -> None:
        ...


    @abstractmethod
    def delete(self, company_id: UUID) -> None:
        ...

    @abstractmethod
    def exists(self, company_id: UUID) -> bool:
        ...

    @abstractmethod
    def exists_owner(self) -> bool:
        ...
