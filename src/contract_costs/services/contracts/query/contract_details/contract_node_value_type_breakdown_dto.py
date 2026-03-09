from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class ContractNodeValueTypeBreakdownDTO:
    value_type_id: UUID
    code: str
    name: str
    direction: str
    net: Decimal
    non_deductible: Decimal
    total: Decimal
    percent_of_direction: Decimal

    def to_dict(self):
        return {
            "value_type_id": str(self.value_type_id),
            "code": self.code,
            "name": self.name,
            "direction": self.direction,
            "net": str(self.net),
            "non_deductible": str(self.non_deductible),
            "total": str(self.total),
            "percent_of_direction": str(self.percent_of_direction),
        }