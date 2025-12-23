from dataclasses import dataclass
from uuid import UUID

from contract_costs.model.contract import ContractStatus

@dataclass(frozen=True)
class ContractExport:
    id: UUID
    name: str
    code: str
