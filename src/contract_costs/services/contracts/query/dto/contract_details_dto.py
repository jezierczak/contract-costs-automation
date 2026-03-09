from dataclasses import dataclass
from datetime import date
from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.services.contracts.query.dto.contract_node_details_dto import ContractNodeDetailsDTO


@dataclass
class ContractDetailsDTO:
    contract_id: UUID
    code: str
    name: str
    owner: Company | None
    client: Company | None
    description: str | None
    status: str
    start_date: date | None
    end_date: date | None

    nodes: list[ContractNodeDetailsDTO]
