from dataclasses import dataclass

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command
from contract_costs.model.financial_record import FinancialRecordStatus


@dataclass(frozen=True, slots=True)
@action_type(ActionType.FINANCIAL_RECORD_MANAGEMENT)
class GenerateFinancialRecordAssignmentBundleCommand(Command):
    invoice_status: FinancialRecordStatus | list[FinancialRecordStatus]