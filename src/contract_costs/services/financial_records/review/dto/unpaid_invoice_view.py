from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from contract_costs.services.financial_records.review.dto.document_view import DocumentView


class UnpaidInvoiceView(BaseModel):
    invoice_id: UUID
    reference: str
    invoice_date: date | None

    buyer_name: str
    buyer_tax_number: str

    seller_name: str
    seller_tax_number: str
    seller_bank_account: str | None

    payment_method: str
    payment_status:str
    due_date: date | None

    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal
    primary_document_path: str | None
    # documents: list[DocumentView]
