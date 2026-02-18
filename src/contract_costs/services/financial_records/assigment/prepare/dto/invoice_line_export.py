from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.amount import VatRate, TaxTreatment

@dataclass(frozen=True)
class FinancialRecordLineExport:
    id: UUID | None
    record_reference: str | None      # None = koszt bez faktury

    item_name: str
    description: str | None
    quantity: Decimal | None
    unit: UnitOfMeasure | None

    net: Decimal
    vat_rate: VatRate
    tax_treatment: TaxTreatment

    contract_code: str | None
    contract_node_code: str | None
    value_type_code: str | None
    agreement_code: str | None
    agreement_node_code: str | None
