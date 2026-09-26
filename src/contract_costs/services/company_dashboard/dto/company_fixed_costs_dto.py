from dataclasses import dataclass
from datetime import date

from contract_costs.services.common.pillars import Pillars


@dataclass(slots=True)
class FixedCostRecordDTO:
    record_id: str
    record_date: date
    item_name: str | None
    description: str | None
    pillars: Pillars


@dataclass(slots=True)
class FixedCostValueTypeDTO:
    value_type_code: str | None
    value_type_name: str | None

    records: list[FixedCostRecordDTO]
    total: Pillars


@dataclass(slots=True)
class CompanyFixedCostsDTO:
    value_types: list[FixedCostValueTypeDTO]
    total: Pillars
