from dataclasses import dataclass, field
from enum import Enum, EnumMeta

from contract_costs.model.amount import TaxTreatment
from contract_costs.services.invoices.dto.export.invoice_export import InvoiceExport
from contract_costs.services.invoices.dto.export.invoice_line_export import InvoiceLineExport
from contract_costs.services.invoices.dto.export.company_export import CompanyExport
from contract_costs.services.invoices.dto.export.contract_export import ContractExport
from contract_costs.services.invoices.dto.export.cost_node_export import CostNodeExport
from contract_costs.services.invoices.dto.export.cost_type_export import CostTypeExport

@dataclass(frozen=True)
class InvoiceAssignmentExportBundle:
    invoices: list[InvoiceExport]
    invoice_lines: list[InvoiceLineExport]

    buyers: list[CompanyExport]
    sellers: list[CompanyExport]

    contracts: list[ContractExport]

    cost_nodes: list[CostNodeExport]
    cost_types: list[CostTypeExport]

    amount_types: dict[str, str] = field(
        default_factory=lambda: InvoiceAssignmentExportBundle.enum_to_dict(TaxTreatment)
    )
    @staticmethod
    def enum_to_dict(enum_cls: EnumMeta) -> dict[str, str]:
        return {e.name: e.value for e in enum_cls}
