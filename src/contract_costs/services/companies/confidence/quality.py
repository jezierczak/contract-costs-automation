from abc import ABC, abstractmethod
from typing import Mapping

from contract_costs.model.company import Company
from contract_costs.services.companies.confidence.fields import CompanyField
from contract_costs.services.companies.confidence.fields import CompanyDataSource
from contract_costs.services.invoices.dto.parse import CompanyInput



class CompanyDataQuality(ABC):
    """
    Describes quality of a SINGLE company data snapshot.

    This object:
    - represents quality, not truth
    - does NOT compare with other companies
    - does NOT mutate anything
    """

    # ---------- FACTORIES ----------

    @classmethod
    @abstractmethod
    def from_company(cls, company_: Company,source: CompanyDataSource | None = None) -> "CompanyDataQuality":
        """
        Create quality snapshot from existing Company (master data).
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_input(cls, input_: CompanyInput, source: CompanyDataSource | None = None) -> "CompanyDataQuality":
        """
        Create quality snapshot from incoming CompanyInput / proposal.
        """
        raise NotImplementedError

    # ---------- SCORING API ----------

    @abstractmethod
    def get_overall_score(self) -> int:
        """
        Overall heuristic score (0–100).
        Used ONLY for bulk decisions / heuristics.
        """
        raise NotImplementedError

    @abstractmethod
    def get_field_score(self, field: CompanyField) -> int:
        """
        Returns confidence score (0–100) for a single field.
        Missing field => 0
        """
        raise NotImplementedError

    @abstractmethod
    def get_field_scores(self) -> Mapping[str, int]:
        """
        Returns confidence scores for all known fields.
        """
        raise NotImplementedError

    @abstractmethod
    def has_field(self, field: CompanyField) -> bool:
        """
        Indicates whether this snapshot contains given field.
        """
        raise NotImplementedError

    @abstractmethod
    def get_value(self, field: CompanyField) -> str | None:
        ...

    @abstractmethod
    def get_source(self) -> CompanyDataSource:
        raise NotImplementedError

    # @abstractmethod
    # def is_identity_conflicting(self) -> bool:
    #     """
    #     Indicates identity conflict (e.g. invalid or conflicting tax number).
    #     """
    #     raise NotImplementedError
