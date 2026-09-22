from datetime import date
from uuid import uuid4

from contract_costs.infrastructure.secrets_cipher import decrypt_secret
from contract_costs.model.company import CompanyType
from contract_costs.model.company_ksef_settings import KsefEnvironment
from contract_costs.services.companies.dto.save_company_ksef_settings_command import (
    SaveCompanyKsefSettingsCommand,
)
from contract_costs.services.companies.save_company_ksef_settings_service import (
    SaveCompanyKsefSettingsService,
)
from tests.builders.company_builder import CompanyBuilder


def _command(*, organization_id, company_id, actor_user_id, certificate_password) -> SaveCompanyKsefSettingsCommand:
    return SaveCompanyKsefSettingsCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        company_id=company_id,
        environment=KsefEnvironment.TEST,
        is_enabled=True,
        certificate_path="C:\\certs\\company.p12",
        certificate_password=certificate_password,
        last_import_from=date(2026, 1, 1),
    )


def test_certificate_password_is_stored_encrypted(monkeypatch, uow, company_repo):
    monkeypatch.setenv("KSEF_SECRETS_KEY", "Heggxv__2jUy7ocBV8xsK5jaAJIyidvCPpAvgWWTPFk=")

    organization_id = uuid4()
    actor_user_id = uuid4()
    company = CompanyBuilder().with_organization_id(organization_id).with_role(CompanyType.OWN).build()
    company_repo.add(company)

    service = SaveCompanyKsefSettingsService()

    settings = service.execute(
        action=_command(
            organization_id=organization_id,
            company_id=company.id,
            actor_user_id=actor_user_id,
            certificate_password="s3cr3t-pin",
        ),
        uow=uow,
    )

    assert settings.certificate_password != "s3cr3t-pin"
    assert decrypt_secret(settings.certificate_password) == "s3cr3t-pin"


def test_blank_password_on_update_keeps_existing_encrypted_value(monkeypatch, uow, company_repo):
    monkeypatch.setenv("KSEF_SECRETS_KEY", "Heggxv__2jUy7ocBV8xsK5jaAJIyidvCPpAvgWWTPFk=")

    organization_id = uuid4()
    actor_user_id = uuid4()
    company = CompanyBuilder().with_organization_id(organization_id).with_role(CompanyType.OWN).build()
    company_repo.add(company)

    service = SaveCompanyKsefSettingsService()

    first = service.execute(
        action=_command(
            organization_id=organization_id,
            company_id=company.id,
            actor_user_id=actor_user_id,
            certificate_password="original-password",
        ),
        uow=uow,
    )

    second = service.execute(
        action=_command(
            organization_id=organization_id,
            company_id=company.id,
            actor_user_id=actor_user_id,
            certificate_password=None,
        ),
        uow=uow,
    )

    assert second.certificate_password == first.certificate_password
    assert decrypt_secret(second.certificate_password) == "original-password"
