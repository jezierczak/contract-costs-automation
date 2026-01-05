from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class InvoiceForAccountantView(BaseModel):
    invoice_id: UUID
    invoice_number: str
    invoice_date: date | None

    buyer_name: str
    buyer_tax_number: str

    seller_name: str
    seller_tax_number: str

    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal
