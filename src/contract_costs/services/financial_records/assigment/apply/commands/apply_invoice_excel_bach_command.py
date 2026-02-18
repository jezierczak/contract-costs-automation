from dataclasses import dataclass
from uuid import UUID


from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import InvoiceExcelBatch


@dataclass(frozen=True)
@action_type(ActionType.APPLY_DOCUMENT)
class ApplyInvoiceExcelBatchCommand(Command):
    organization_id: UUID
    actor_user_id: UUID
    batch: InvoiceExcelBatch
