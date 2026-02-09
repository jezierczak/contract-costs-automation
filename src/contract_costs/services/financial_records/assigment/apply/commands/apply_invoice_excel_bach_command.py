from dataclasses import dataclass
from uuid import UUID

from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import InvoiceExcelBatch


@dataclass(frozen=True)
class ApplyInvoiceExcelBatchCommand:
    organization_id: UUID
    actor_user_id: UUID
    batch: InvoiceExcelBatch
