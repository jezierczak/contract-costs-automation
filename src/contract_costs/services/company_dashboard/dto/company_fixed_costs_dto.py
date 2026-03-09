from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class FixedCostRecordDTO:
    record_id: UUID
    record_date: date
    description: str | None
    amount: Decimal
    tax_treatment: str


@dataclass(slots=True)
class FixedCostValueTypeDTO:
    value_type_code: str
    value_type_name: str

    records: list[FixedCostRecordDTO]
    total: Decimal


@dataclass(slots=True)
class FixedCostContractDTO:
    contract_id: UUID
    contract_code: str

    value_types: list[FixedCostValueTypeDTO]
    total: Decimal


@dataclass(slots=True)
class CompanyFixedCostsDTO:
    contracts: list[FixedCostContractDTO]
    total: Decimal