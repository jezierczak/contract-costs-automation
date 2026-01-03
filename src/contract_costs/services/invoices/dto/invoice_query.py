from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.invoice import PaymentStatus, PaymentMethod


@dataclass(frozen=True)
class InvoiceLineView:
    item_name: str
    quantity: Decimal
    unit: str

    net: Decimal
    vat: Decimal
    gross: Decimal

    contract_code: str | None
    cost_node_code: str | None
    cost_type_code: str | None


@dataclass(frozen=True)
class InvoiceDetailsView:
    invoice_number: str
    status: str
    invoice_date: date | None
    selling_date: date | None

    buyer_name: str
    buyer_tax_number: str

    seller_name: str
    seller_tax_number: str

    payment_status: str
    payment_method: str
    due_date: date | None

    lines: list[InvoiceLineView]

    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal
    total_not_evidenced: Decimal
