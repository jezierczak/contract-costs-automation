from dataclasses import dataclass

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import InvoiceExcelBatch


@dataclass(frozen=True, slots=True)
@action_type(ActionType.FINANCIAL_RECORD_MANAGEMENT)
class ResolveFinancialRecordExcelBatchCommand(Command):
    batch: InvoiceExcelBatch