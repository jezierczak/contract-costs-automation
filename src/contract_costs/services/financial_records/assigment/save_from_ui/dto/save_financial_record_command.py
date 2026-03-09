from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.amount import Amount
from contract_costs.model.financial_record import PaymentMethod, PaymentStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure


@dataclass(frozen=True)
class SaveFinancialRecordCommand:

    organization_id: UUID
    actor_user_id: UUID

    record_id: UUID | None

    reference: str
    invoice_date: date | None
    selling_date: date | None

    buyer_tax_number: str
    seller_tax_number: str

    payment_method: PaymentMethod
    payment_status: PaymentStatus

    lines: list["SaveFinancialRecordLine"]

@dataclass(frozen=True)
class SaveFinancialRecordLine:

    record_line_id: UUID | None

    item_name: str
    description: str | None
    quantity: Decimal
    unit: UnitOfMeasure
    amount: Amount

    contract_id: UUID | None
    contract_node_id: UUID | None
    value_type_id: UUID | None
    agreement_id: UUID | None
    agreement_node_id: UUID | None