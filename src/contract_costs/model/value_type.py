from dataclasses import dataclass
from uuid import UUID

from contract_costs.model.value_direction import ValueDirection


# class CostType(Enum):
#     MATERIAL = "material"
#     SERVICE = "services"
#     SUBCONTRACTOR = "subcontractor"
#     LABOR = "labor"
#     EQUIPMENT = "equipment"
#     TRANSPORT = "transport"
#     OTHER = "other"


@dataclass
class ValueType:
    id: UUID
    code: str            # unikalny, np. MATERIAL, SALARY
    name: str            # czytelna nazwa
    description: str | None
    direction: ValueDirection  # COST | REVENUE
    is_active: bool = True