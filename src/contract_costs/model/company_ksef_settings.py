from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from contract_costs.model.base_entity import BaseEntity


class KsefEnvironment(Enum):
    TEST = "test"
    DEMO = "demo"
    PROD = "prod"


@dataclass(slots=True)
class CompanyKsefSettings(BaseEntity):
    id: UUID
    company_id: UUID
    environment: KsefEnvironment
    is_enabled: bool
    certificate_path: str | None
    certificate_password: str | None
    last_import_from: date | None
    last_import_at: datetime | None
    last_error: str | None
