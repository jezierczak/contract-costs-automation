from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.base_entity import BaseEntity


@dataclass(slots=True)
class FinancialRecordPayment(BaseEntity):
    id: UUID

    financial_record_id: UUID

    amount: Decimal
    paid_date: date
