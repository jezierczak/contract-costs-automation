from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import RecordIngestBatch


@dataclass(frozen=True, slots=True)
class BaseFinancialRecordIngestCommand(Command):
    batch: RecordIngestBatch

@action_type(ActionType.FINANCIAL_RECORD_MANAGEMENT)
class IngestFinancialRecordFromDocumentCommand(
    BaseFinancialRecordIngestCommand
):
    pass

@action_type(ActionType.FINANCIAL_RECORD_MANAGEMENT)
class IngestFinancialRecordFromExcelCommand(
    BaseFinancialRecordIngestCommand
):
    pass

@action_type(ActionType.FINANCIAL_RECORD_MANAGEMENT)
class IngestFinancialRecordFromUICommand(BaseFinancialRecordIngestCommand):
    pass