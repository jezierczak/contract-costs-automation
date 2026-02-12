from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.query import Query
from contract_costs.model.contract import ContractType


@dataclass(frozen=True)
class ListContractsQuery(Query):
    contract_type: ContractType | None
