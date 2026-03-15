from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.query import Query
from contract_costs.model.company import CompanyType


from dataclasses import dataclass

from contract_costs.model.company import CompanyType


@dataclass(frozen=True,slots=True)
@action_type(ActionType.COMPANY_MANAGEMENT)
class CompanyQuery(Query):
    # =====================
    # IDENTYFIKATORY (STRICT)
    # =====================
    tax_number: str | None = None
    company_id: str | UUID | None = None

    # =====================
    # FILTRY LOGICZNE
    # =====================
    own_only: bool = False
    include_inactive: bool = False

    # =====================
    # FILTRY ENUM
    # =====================
    role: CompanyType | None = None

    # =====================
    # FILTRY TEKSTOWE (LIKE)
    # =====================
    search: str | None = None

