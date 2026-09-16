from uuid import UUID

from contract_costs.model.company_ksef_settings import CompanyKsefSettings
from contract_costs.repository.company_ksef_settings_repository import CompanyKsefSettingsRepository


class InMemoryCompanyKsefSettingsRepository(CompanyKsefSettingsRepository):
    def __init__(self) -> None:
        self._items: dict[tuple[UUID, UUID], CompanyKsefSettings] = {}

    def get_by_company_id(
        self,
        *,
        organization_id: UUID,
        company_id: UUID,
    ) -> CompanyKsefSettings | None:
        return self._items.get((organization_id, company_id))

    def add(
        self,
        *,
        organization_id: UUID,
        settings: CompanyKsefSettings,
    ) -> None:
        self._items[(organization_id, settings.company_id)] = settings

    def update(
        self,
        *,
        organization_id: UUID,
        settings: CompanyKsefSettings,
    ) -> None:
        self._items[(organization_id, settings.company_id)] = settings
