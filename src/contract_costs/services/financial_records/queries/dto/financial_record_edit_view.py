from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from contract_costs.services.financial_records.queries.dto.attached_document_view import AttachedDocumentView

@dataclass(frozen=True)
class ContractNodeView:
    id: str
    code: str
    name: str | None = None
    depth: int =0

@dataclass(frozen=True)
class InvoiceLineEditView:
    record_line_id: str
    item_name: str
    description: str | None

    quantity: Decimal
    unit: str

    amount_value: Decimal
    vat_rate: str
    amount_type: str
    tax_treatment: str

    # IDs (UI)
    contract_id: str | None
    contract_node_id: str | None
    value_type_id: str | None

    agreement_id: str | None
    agreement_node_id: str | None

    # dropdown preload
    contract_nodes: list[ContractNodeView]
    agreement_nodes: list[ContractNodeView]

@dataclass(frozen=True)
class FinancialRecordEditView:

    id: str
    reference: str

    invoice_date: date | None
    selling_date: date | None

    payment_method: str
    payment_status: str
    due_date: date | None
    paid_date: date | None

    buyer_name: str
    buyer_tax_number: str

    seller_name: str
    seller_tax_number: str

    tags: str | None

    lines: list[InvoiceLineEditView]

    documents: list[AttachedDocumentView]

    source_confidence: int | None
    source_breakdown: dict | None