from  dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from contract_costs.model.amount import Amount
from contract_costs.model.base_entity import BaseEntity
from contract_costs.model.unit_of_measure import UnitOfMeasure


@dataclass(slots=True)
class FinancialRecordLine(BaseEntity):
    id: UUID

    financial_record_id: UUID | None   # zamiast invoice_id
    contract_id: UUID | None
    contract_node_id: UUID | None
    agreement_id: UUID | None
    agreement_node_id: UUID | None
    value_type_id: UUID | None

    item_name: str
    quantity: Decimal | None
    unit: UnitOfMeasure | None

    amount: Amount
    description: str | None

