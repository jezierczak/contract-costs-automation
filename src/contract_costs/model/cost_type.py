from dataclasses import dataclass
from uuid import UUID

# from enum import Enum

# class CostType(Enum):
#     MATERIAL = "material"
#     SERVICE = "services"
#     SUBCONTRACTOR = "subcontractor"
#     LABOR = "labor"
#     EQUIPMENT = "equipment"
#     TRANSPORT = "transport"
#     OTHER = "other"


@dataclass
class CostType:
    id: UUID
    code: str            # unikalny, np. MATERIAL, SALARY
    name: str            # czytelna nazwa
    is_active: bool = True