from dataclasses import dataclass, field
from enum import Enum
from typing import Type

from contract_costs.model.amount import TaxTreatment, VatRate
from contract_costs.model.invoice import PaymentMethod, PaymentStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.invoices.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.assigment.prepare.dto.invoice_export import InvoiceExport
from contract_costs.services.invoices.assigment.prepare.dto.invoice_line_export import InvoiceLineExport
from contract_costs.services.invoices.assigment.prepare.dto.company_export import CompanyExport
from contract_costs.services.invoices.assigment.prepare.dto.contract_export import ContractExport
from contract_costs.services.invoices.assigment.prepare.dto.cost_node_export import CostNodeExport
from contract_costs.services.invoices.assigment.prepare.dto.cost_type_export import CostTypeExport

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
    payment_methods: dict[str, str] = field(
        default_factory=lambda: InvoiceAssignmentExportBundle.enum_to_dict(PaymentMethod)
    )
    payment_status: dict[str, str] = field(
        default_factory=lambda: InvoiceAssignmentExportBundle.enum_to_dict(PaymentStatus)
    )
    units: dict[str, str] = field(
        default_factory=lambda: InvoiceAssignmentExportBundle.enum_to_dict(UnitOfMeasure)
    )
    vat_rates: dict[str, str] = field(
        default_factory=lambda: InvoiceAssignmentExportBundle.enum_to_dict(VatRate)
    )
    actions: dict[str, str] = field(
        default_factory=lambda: InvoiceAssignmentExportBundle.enum_to_dict(InvoiceCommand)
    )
    @staticmethod
    def enum_to_dict(enum_cls: Type[Enum]) -> dict[str, str]:
        return {e.name: str(e.value) for e in enum_cls}
