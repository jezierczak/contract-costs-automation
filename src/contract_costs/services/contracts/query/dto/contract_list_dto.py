from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from contract_costs.services.contracts.financials.contract_financials import ContractFinancials


@dataclass
class ContractListDTO:
    contract_id: UUID
    code: str
    name: str
    status: str
    is_active: bool

    planned_budget: Decimal
    progress: Decimal | None

    net: Decimal
    non_deduction: Decimal
    revenue_non_deductible:Decimal

    revenue: Decimal

    financials: ContractFinancials
