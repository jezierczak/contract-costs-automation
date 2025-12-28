from  dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from contract_costs.model.amount import Amount
from contract_costs.model.unit_of_measure import UnitOfMeasure


@dataclass
class InvoiceLine:
    id: UUID
    invoice_id: UUID | None
    contract_id: UUID | None
    cost_node_id: UUID | None
    cost_type_id: UUID | None
    item_name: str
    quantity: Decimal | None
    unit: UnitOfMeasure
    amount: Amount
    description: str | None

