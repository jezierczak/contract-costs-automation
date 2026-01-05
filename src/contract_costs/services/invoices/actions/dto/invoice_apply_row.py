from pydantic import BaseModel
from uuid import UUID


class InvoiceApplyRow(BaseModel):
    invoice_id: UUID
    selected: bool
