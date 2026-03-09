from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from contract_costs.services.financial_records.queries.dto.attached_document_view import AttachedDocumentView


@dataclass(frozen=True)
class InvoiceLineView:
    item_name: str
    quantity: Decimal
    unit: str

    net: Decimal
    vat: Decimal
    gross: Decimal
    not_evidenced:Decimal

    contract_code: str | None
    cost_node_code: str | None
    cost_type_code: str | None

    # NEW
    agreement_code: str | None = None
    agreement_node_code: str | None = None

    # optional UI field
    description: str | None = None


@dataclass(frozen=True)
class FinancialRecordDetailsView:
    id: str
    reference: str
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
    paid_date: date | None

    tags: str | None

    lines: list[InvoiceLineView]

    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal
    total_not_evidenced: Decimal

    contract_codes: str | None
    direction: str | None

    documents: list[AttachedDocumentView]
