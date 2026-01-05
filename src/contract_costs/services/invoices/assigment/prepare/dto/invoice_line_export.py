from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.amount import VatRate, TaxTreatment

@dataclass(frozen=True)
class InvoiceLineExport:
    id: UUID | None
    invoice_number: str | None      # None = koszt bez faktury

    item_name: str
    description: str | None
    quantity: Decimal | None
    unit: UnitOfMeasure | None

    net: Decimal
    vat_rate: VatRate
    tax_treatment: TaxTreatment

    contract_id: UUID | None
    cost_node_id: UUID | None
    cost_type_id: UUID | None
