from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.company import Company


class CompanyRepository(ABC):

    # --- basic CRUD ---

    @abstractmethod
    def add(self, company: Company) -> None:
        ...

    @abstractmethod
    def update(self, company: Company) -> None:
        ...

    @abstractmethod
    def delete(self, company_id: UUID, organization_id: UUID) -> None:
        ...

    @abstractmethod
    def get(self, company_id: UUID, organization_id: UUID) -> Company | None:
        ...

    @abstractmethod
    def exists(self, company_id: UUID, organization_id: UUID) -> bool:
        ...

    @abstractmethod
    def list_all(self, organization_id: UUID) -> list[Company]:
        ...


    # --- identity / ownership ---

    @abstractmethod
    def get_by_tax_number(self, tax_number: str, organization_id: UUID) -> Company | None:
        """
        Exact match by normalized tax number.
        """
        ...

    @abstractmethod
    def get_owners(self, organization_id: UUID) -> list[Company]:
        """
        Returns all companies with role OWN.
        """
        ...

    @abstractmethod
    def exists_owner(self, organization_id: UUID) -> bool:
        """
        True if at least one OWN company exists.
        """
        ...


    # --- candidate search (USED BY CandidateProvider) ---

    @abstractmethod
    def find_by_bank_account(self, organization_id: UUID, bank_account_number: str) -> list[Company]:
        """
        Exact match by normalized bank account number (26 digits).
        Can return multiple companies.
        """
        ...

    @abstractmethod
    def find_by_email(self, organization_id: UUID, email: str) -> list[Company]:
        """
        Exact match by normalized (lowercase) email.
        """
        ...

    @abstractmethod
    def find_by_phone(self, organization_id: UUID, phone_number: str) -> list[Company]:
        """
        Exact match by normalized phone number (9 digits).
        """
        ...

    @abstractmethod
    def find_by_name_like(self, organization_id: UUID, name: str) -> list[Company]:
        """
        Fuzzy / LIKE search by company name.
        Used only as fallback.
        """
        ...
    @abstractmethod
    def find_by_street_tokens(self, organization_id: UUID, tokens: list[str]) -> list[Company]:
        ...

