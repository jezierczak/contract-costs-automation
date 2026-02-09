from dataclasses import dataclass
from uuid import UUID

from contract_costs.model.company import CompanyType
from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.model.value_direction import ValueDirection


@dataclass(frozen=True)
class FinancialRecordAssignmentFacts:
    record_id: UUID
    invoice_lines: list[FinancialRecordLine]
    buyer_role: CompanyType
    seller_role: CompanyType
    value_type_directions: dict[UUID, ValueDirection]