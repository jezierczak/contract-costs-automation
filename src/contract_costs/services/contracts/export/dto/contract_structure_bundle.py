from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TypedDict

from contract_costs.model.contract import Contract
from contract_costs.model.cost_node import CostNode

class ContractStructureRow(TypedDict):
    code: str
    name:str
    owner_nip: str
    client_nip: str | None
    description:str | None
    start_date: date | None
    end_date: date | None
    budget: Decimal | None
    path: str
    status: str

class CostNodeStructureRow(TypedDict):
    code:str
    name: str
    parent_code: str | None
    budget: Decimal | None
    quantity:Decimal | None
    unit:str | None
    is_active: bool

@dataclass
class ContractStructureBundle:
    contract: ContractStructureRow | None
    cost_nodes: list[CostNodeStructureRow]