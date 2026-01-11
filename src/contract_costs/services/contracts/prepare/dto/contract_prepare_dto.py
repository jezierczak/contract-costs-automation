from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class ContractPrepareDTO:
    code: str
    name: str
    owner_nip: str
    client_nip: str | None
    description: str | None
    start_date: date | None
    end_date: date | None
    budget: Decimal | None
    path: str
    status: str
