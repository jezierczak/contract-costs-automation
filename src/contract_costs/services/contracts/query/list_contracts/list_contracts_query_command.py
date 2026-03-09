from dataclasses import dataclass

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.query import Query
from contract_costs.model.contract import ContractType, ContractStatus


@action_type(ActionType.CONTRACT_VIEW)
@dataclass(frozen=True)
class ListContractsQuery(Query):
    contract_type: ContractType | None = None
    status: ContractStatus | None = None
    search: str | None = None
