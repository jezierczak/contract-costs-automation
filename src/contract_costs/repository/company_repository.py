from uuid import UUID
from abc import ABC, abstractmethod
from typing import Iterable

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
    def delete(self, company_id: UUID) -> None:
        ...

    @abstractmethod
    def get(self, company_id: UUID) -> Company | None:
        ...

    @abstractmethod
    def exists(self, company_id: UUID) -> bool:
        ...

    @abstractmethod
    def list_all(self) -> list[Company]:
        ...


    # --- identity / ownership ---

    @abstractmethod
    def get_by_tax_number(self, tax_number: str) -> Company | None:
        """
        Exact match by normalized tax number.
        """
        ...

    @abstractmethod
    def get_owners(self) -> list[Company]:
        """
        Returns all companies with role OWN.
        """
        ...

    @abstractmethod
    def exists_owner(self) -> bool:
        """
        True if at least one OWN company exists.
        """
        ...


    # --- candidate search (USED BY CandidateProvider) ---

    @abstractmethod
    def find_by_bank_account(self, bank_account: str) -> list[Company]:
        """
        Exact match by normalized bank account number (26 digits).
        Can return multiple companies.
        """
        ...

    @abstractmethod
    def find_by_email(self, email: str) -> list[Company]:
        """
        Exact match by normalized (lowercase) email.
        """
        ...

    @abstractmethod
    def find_by_phone(self, phone_number: str) -> list[Company]:
        """
        Exact match by normalized phone number (9 digits).
        """
        ...

    @abstractmethod
    def find_by_name_like(self, name: str) -> list[Company]:
        """
        Fuzzy / LIKE search by company name.
        Used only as fallback.
        """
        ...
    @abstractmethod
    def find_by_street_tokens(self, tokens: list[str]) -> list[Company]:
        ...

