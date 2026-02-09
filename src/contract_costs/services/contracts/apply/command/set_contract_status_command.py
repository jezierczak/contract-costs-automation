from dataclasses import dataclass
from uuid import UUID
from contract_costs.model.contract import ContractStatus

@dataclass(frozen=True)
class SetContractStatusCommand:
    organization_id: UUID
    actor_user_id: UUID
    contract_id: UUID
    new_status: ContractStatus
