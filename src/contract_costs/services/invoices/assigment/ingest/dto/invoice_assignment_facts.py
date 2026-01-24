from dataclasses import dataclass
from uuid import UUID

from contract_costs.model.company import CompanyType
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.value_direction import ValueDirection


@dataclass(frozen=True)
class InvoiceAssignmentFacts:
    invoice_id: UUID
    invoice_lines: list[InvoiceLine]
    buyer_role: CompanyType
    seller_role: CompanyType
    value_type_directions: dict[UUID, ValueDirection]