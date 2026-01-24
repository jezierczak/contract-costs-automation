from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class ContractSnapshotValueRowDTO:
    snapshot_id: UUID
    snapshot_date: date

    contract_id: UUID
    node_id: UUID

    value_type_code: str
    direction: str  # cost / revenue

    net: Decimal
    vat: Decimal
    gross: Decimal
    non_deductible: Decimal
