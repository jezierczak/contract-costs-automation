from dataclasses import dataclass

from contract_costs.model.company import CompanyType


from dataclasses import dataclass

from contract_costs.model.company import CompanyType


@dataclass(frozen=True)
class CompanyQuery:
    # =====================
    # IDENTYFIKATORY (STRICT)
    # =====================
    tax_number: str | None = None

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

