from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class InvoiceReviewItemView(BaseModel):
    invoice_id: UUID
    invoice_number: str
    invoice_date: date | None

    buyer_name: str
    buyer_tax_number: str
    seller_name: str
    seller_tax_number: str
    seller_bank_account: str | None

    status: str
    payment_method: str
    payment_status: str
    due_date: date | None

    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal
    total_not_evidenced: Decimal
    
    scan_filename: str | None

    contract_codes: str | None
    direction: str | None
