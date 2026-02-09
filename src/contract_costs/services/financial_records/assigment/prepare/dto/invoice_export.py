from dataclasses import dataclass
from datetime import date, datetime

from contract_costs.model.financial_record import FinancialRecordStatus, PaymentMethod, PaymentStatus
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand


@dataclass(frozen=True)
class FinancialRecordExport:
    action: InvoiceCommand | None
    record_id: str | None
    # invoice_number: str | None
    reference: str
    invoice_date: date | None
    selling_date: date | None

    buyer_tax_number: str | None
    seller_tax_number: str | None

    payment_method: PaymentMethod
    payment_status: PaymentStatus
    status: FinancialRecordStatus

    due_date: date | None
    paid_date: date | None
    primary_document_path: str | None
    tags: set[str]
    timestamp: datetime
