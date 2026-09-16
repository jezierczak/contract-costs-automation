from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.model.company_ksef_settings import CompanyKsefSettings


class CompanyKsefSettingsRepository(ABC):
    @abstractmethod
    def get_by_company_id(
        self,
        *,
        organization_id: UUID,
        company_id: UUID,
    ) -> CompanyKsefSettings | None:
        ...

    @abstractmethod
    def add(
        self,
        *,
        organization_id: UUID,
        settings: CompanyKsefSettings,
    ) -> None:
        ...

    @abstractmethod
    def update(
        self,
        *,
        organization_id: UUID,
        settings: CompanyKsefSettings,
    ) -> None:
        ...
