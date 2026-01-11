from dataclasses import dataclass
from uuid import UUID
from contract_costs.model.contract import ContractStatus

@dataclass(frozen=True)
class SetContractStatusCommand:
    contract_id: UUID
    new_status: ContractStatus
