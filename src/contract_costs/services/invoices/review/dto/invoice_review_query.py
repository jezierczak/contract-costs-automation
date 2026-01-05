from datetime import date

from pydantic import BaseModel

from contract_costs.model.invoice import InvoiceStatus, PaymentStatus


class InvoiceReviewQuery(BaseModel):
    statuses: list[InvoiceStatus] | None = None
    payment_statuses: list[PaymentStatus] | None = None

    from_date: date | None = None
    to_date: date | None = None

    only_ready_for_accountant: bool | None = None