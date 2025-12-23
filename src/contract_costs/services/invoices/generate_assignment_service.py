from dataclasses import replace
from pathlib import Path

from contract_costs.model.invoice import InvoiceStatus, Invoice
from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.repository.cost_type_repository import CostTypeRepository

from contract_costs.services.invoices.export.invoice_assignment_exporter import (
    InvoiceAssignmentExporter,
)

from contract_costs.services.invoices.dto.export.assignment_export_bundle import (
    InvoiceAssignmentExportBundle,
)
from contract_costs.services.invoices.dto.export.invoice_export import InvoiceExport
from contract_costs.services.invoices.dto.export.invoice_line_export import InvoiceLineExport
from contract_costs.services.invoices.dto.export.company_export import CompanyExport
from contract_costs.services.invoices.dto.export.contract_export import ContractExport
from contract_costs.services.invoices.dto.export.cost_node_export import CostNodeExport
from contract_costs.services.invoices.dto.export.cost_type_export import CostTypeExport

class GenerateInvoiceAssignmentService:

    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        invoice_line_repository: InvoiceLineRepository,
        company_repository: CompanyRepository,
        contract_repository: ContractRepository,
        cost_node_repository: CostNodeRepository,
        cost_type_repository: CostTypeRepository,
        exporter: InvoiceAssignmentExporter,
    ) -> None:
        self._invoice_repo = invoice_repository
        self._invoice_line_repo = invoice_line_repository
        self._company_repo = company_repository
        self._contract_repo = contract_repository
        self._cost_node_repo = cost_node_repository
        self._cost_type_repo = cost_type_repository
        self._exporter = exporter

    def execute(self, invoice_status: InvoiceStatus | list[InvoiceStatus], output_path: Path) -> None:
        #  Dane główne

        # invoice_status = InvoiceStatus(status)
        invoices: list[Invoice] = self._invoice_repo.get_for_assignment(invoice_status)

        invoice_ids = [i.id for i in invoices]

        invoice_numbers_from_ids = {i.id:i.invoice_number for i in invoices}

        updated_invoices: list[Invoice] = []

        for invoice in invoices:
            if invoice.status != InvoiceStatus.IN_PROGRESS:
                updated = replace(invoice, status=InvoiceStatus.IN_PROGRESS)
                self._invoice_repo.update(updated)
                updated_invoices.append(updated)
            else:
                updated_invoices.append(invoice)

        invoice_lines = self._invoice_line_repo.list_by_invoice_ids(invoice_ids)
        invoice_lines.extend(self._invoice_line_repo.list_by_null_invoice())


        #  Companies (buyer + seller)

        company_buyers = {
            inv.buyer_id for inv in updated_invoices}
        company_sellers= {
            inv.seller_id for inv in updated_invoices
        }

        buyers = [
            CompanyExport(
                id=c.id,
                name=c.name,
                tax_number=c.tax_number,
            )
            for c in (self._company_repo.get(cid) for cid in company_buyers)
            if c is not None
        ]

        sellers = [
            CompanyExport(
                id=c.id,
                name=c.name,
                tax_number=c.tax_number,
            )
            for c in (self._company_repo.get(cid) for cid in company_sellers)
            if c is not None
        ]

        #  Contracts
        contracts = [
            ContractExport(
                id=c.id,
                name=c.name,
                code=c.code,
            )
            for c in self._contract_repo.list()
        ]

        #  Cost nodes
        cost_nodes = [
            CostNodeExport(
                id=n.id,
                contract_id=n.contract_id,
                parent_id=n.parent_id,
                code=n.code,
                name=n.name,
                budget=n.budget,
            )
            for n in self._cost_node_repo.list_nodes()
        ]

        #  Cost types
        cost_types = [
            CostTypeExport(
                id=ct.id,
                code=ct.code,
                name=ct.name,
            )
            for ct in self._cost_type_repo.list()
        ]

        #  Mapowanie faktur
        invoice_exports = [
            InvoiceExport(
                invoice_number=i.invoice_number,
                invoice_date=i.invoice_date,
                selling_date=i.selling_date,
                buyer_tax_number=self._company_repo.get(i.buyer_id).tax_number,
                seller_tax_number=self._company_repo.get(i.seller_id).tax_number,
                payment_method=i.payment_method,
                payment_status=i.payment_status,
                status=i.status,
                due_date=i.due_date,
                timestamp=i.timestamp,
            )
            for i in updated_invoices
        ]

        # ⃣Mapowanie linii
        if invoice_lines is not None and len(invoice_lines) > 0:
            # for ll in invoice_lines:
            #     print(ll)
            line_exports = [
                InvoiceLineExport(
                    id = l.id,
                    invoice_number=invoice_numbers_from_ids.get(l.invoice_id) if l.invoice_id else "",
                    item_name = l.item_name,
                    description=l.description,
                    quantity=l.quantity,
                    unit=l.unit,
                    net=l.amount.value,
                    vat_rate=l.amount.vat_rate.value,
                    tax_treatment=l.amount.tax_treatment,
                    contract_id=l.contract_id,
                    cost_node_id=l.cost_node_id,
                    cost_type_id=l.cost_type_id,
                )
                for l in invoice_lines
            ]
        else:
            line_exports = []

        bundle = InvoiceAssignmentExportBundle(
            invoices=invoice_exports,
            invoice_lines=line_exports,
            buyers=buyers,
            sellers=sellers,
            contracts=contracts,
            cost_nodes=cost_nodes,
            cost_types=cost_types,
        )

        self._exporter.export(bundle,output_path=output_path)
