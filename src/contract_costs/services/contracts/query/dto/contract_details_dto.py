from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.services.contracts.financials.contract_financials import ContractFinancials
from contract_costs.services.contracts.financials.contract_timeline import ContractTimeline

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
    budget:Decimal | None
    time_progress: Decimal | None
    overall_progress: Decimal | None
    executed_value: Decimal | None
    cost_total: Decimal | None
    revenue_total: Decimal | None
    margin: Decimal | None
    margin_percent: Decimal | None

    nodes: list[ContractNodeDetailsDTO]

    financials: ContractFinancials
    timeline: ContractTimeline
