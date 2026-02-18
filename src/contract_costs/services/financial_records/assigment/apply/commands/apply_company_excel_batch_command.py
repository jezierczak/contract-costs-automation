from dataclasses import dataclass

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command
from contract_costs.services.financial_records.assigment.prepare.dto.company_export import CompanyExport


@dataclass(frozen=True, slots=True)
@action_type(ActionType.COMPANY_MANAGEMENT)
class ApplyCompanyExcelBatchCommand(Command):
    companies: list[CompanyExport]