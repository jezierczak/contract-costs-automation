from dataclasses import dataclass
from datetime import date
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command
from contract_costs.model.company_ksef_settings import KsefEnvironment


@action_type(ActionType.OWNER_COMPANY_MANAGEMENT)
@dataclass(frozen=True)
class SaveCompanyKsefSettingsCommand(Command):
    company_id: UUID
    environment: KsefEnvironment
    is_enabled: bool
    certificate_path: str | None
    certificate_password: str | None
    last_import_from: date | None
