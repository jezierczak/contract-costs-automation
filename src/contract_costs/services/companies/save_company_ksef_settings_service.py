from dataclasses import replace
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.infrastructure.secrets_cipher import encrypt_secret
from contract_costs.model.company import CompanyType
from contract_costs.model.company_ksef_settings import CompanyKsefSettings
from contract_costs.services.companies.dto.save_company_ksef_settings_command import (
    SaveCompanyKsefSettingsCommand,
)
from contract_costs.unit_of_work import UnitOfWork


class SaveCompanyKsefSettingsService(ActionHandler[SaveCompanyKsefSettingsCommand, CompanyKsefSettings]):
    def __init__(
        self,
        *,
        clock: Callable = utc_now,
        id_generator: Callable = new_uuid,
    ) -> None:
        self._clock = clock
        self._id_generator = id_generator

    def execute(
        self,
        *,
        action: SaveCompanyKsefSettingsCommand,
        uow: UnitOfWork,
    ) -> CompanyKsefSettings:
        company = uow.companies.get(
            action.company_id,
            action.organization_id,
        )
        if company is None:
            raise ValueError("Company does not exist")
        if company.role != CompanyType.OWN:
            raise ValueError("KSeF settings are available only for own companies")

        repo = uow.company_ksef_settings
        current = repo.get_by_company_id(
            organization_id=action.organization_id,
            company_id=action.company_id,
        )

        now = self._clock()

        # Puste pole hasła w formularzu = "zostaw bez zmian", żeby nie trzeba
        # było wpisywać hasła od nowa przy każdym zapisie pozostałych ustawień.
        encrypted_password = (
            encrypt_secret(action.certificate_password)
            if action.certificate_password
            else (current.certificate_password if current else None)
        )

        if current is None:
            settings = CompanyKsefSettings(
                id=self._id_generator(),
                organization_id=action.organization_id,
                company_id=action.company_id,
                environment=action.environment,
                is_enabled=action.is_enabled,
                certificate_path=action.certificate_path,
                certificate_password=encrypted_password,
                last_import_from=action.last_import_from,
                last_import_at=None,
                last_error=None,
                created_at=now,
                created_by_user_id=action.actor_user_id,
                updated_at=now,
                updated_by_user_id=action.actor_user_id,
            )
            repo.add(
                organization_id=action.organization_id,
                settings=settings,
            )
            return settings

        updated = replace(
            current,
            environment=action.environment,
            is_enabled=action.is_enabled,
            certificate_path=action.certificate_path,
            certificate_password=encrypted_password,
            last_import_from=action.last_import_from,
            updated_at=now,
            updated_by_user_id=action.actor_user_id,
        )
        repo.update(
            organization_id=action.organization_id,
            settings=updated,
        )
        return updated
