from pathlib import Path

from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.worksheet import Worksheet

from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.services.invoices.dto.export.assignment_export_bundle import InvoiceAssignmentExportBundle
from contract_costs.services.invoices.export.invoice_assignment_exporter import InvoiceAssignmentExporter

import contract_costs.config as cfg

class ExcelInvoiceAssignmentExporter(InvoiceAssignmentExporter):
    def __init__(self,
                 contract_repository: ContractRepository,
                 cost_node_repository: CostNodeRepository,
                 cost_type_repository:CostTypeRepository):
        self._contract_repository = contract_repository
        self._cost_node_repository = cost_node_repository
        self._cost_type_repository = cost_type_repository

    def export(
            self,
            bundle: InvoiceAssignmentExportBundle,
            output_path: Path
    ) -> None:
        wb = Workbook()

        invoices_ws = self._write_invoices(wb, bundle.invoices)
        lines_ws = self._write_invoice_lines(wb, bundle.invoice_lines)
        buyers_ws = self._write_buyers(wb, bundle.buyers)
        sellers_ws = self._write_sellers(wb, bundle.sellers)
        contracts_ws = self._write_contracts(wb, bundle.contracts)
        cost_nodes_ws = self._write_cost_nodes(wb, bundle.cost_nodes)
        cost_types_ws = self._write_cost_types(wb, bundle.cost_types)
        tax_treatment_ws = self._write_tax_treatment(wb,bundle.amount_types)

        self._apply_dropdowns(
            invoices_ws=invoices_ws,
            lines_ws=lines_ws,
            buyers_ws=buyers_ws,
            sellers_ws=sellers_ws,
            contracts_ws=contracts_ws,
            cost_nodes_ws=cost_nodes_ws,
            cost_types_ws=cost_types_ws,
            tax_treatments_ws=tax_treatment_ws
        )

        # opcjonalnie: usuń domyślny pusty sheet
        if "Sheet" in wb.sheetnames:
            del wb["Sheet"]

        wb.save(output_path)

    def _write_invoices(self, wb: Workbook, invoices) -> Worksheet:
        ws = wb.create_sheet(cfg.INVOICE_METADATA_SHEET_NAME)

        headers = [
            "invoice_number",
            "invoice_date",
            "selling_date",
            "buyer_NIP",
            "seller_NIP",
            "payment_method",
            "payment_status",
            "status",
            "due_date",
            "timestamp",
        ]
        ws.append(headers)

        for i in invoices:
            ws.append([
                i.invoice_number,
                i.invoice_date,
                i.selling_date,
                str(i.buyer_tax_number),
                str(i.seller_tax_number),
                i.payment_method.value,
                i.payment_status.value,
                i.status.value,
                i.due_date,
                i.timestamp,
            ])

        return ws

    def _write_invoice_lines(self, wb: Workbook, lines) -> Worksheet:
        ws = wb.create_sheet(cfg.INVOICE_ITEMS_SHEET_NAME)

        headers = [
            "id",
            "invoice_number",
            "item_name",
            "description",
            "quantity",
            "unit",
            "net",
            "vat_rate",
            "tax_treatment",
            "contract_id",
            "cost_node_id",
            "cost_type_id",
        ]
        ws.append(headers)

        contracts = {
            c.id: c.code
            for c in self._contract_repository.list()
        }

        cost_nodes = {
            n.id: n.code
            for n in self._cost_node_repository.list_nodes()
        }

        cost_types = {
            t.id: t.code
            for t in self._cost_type_repository.list()
        }

        for l in lines:
            ws.append([
                str(l.id),
                str(l.invoice_number) if l.invoice_number else None,
                l.item_name,
                l.description,
                l.quantity,
                l.unit.value,
                l.net,
                l.vat_rate,
                l.tax_treatment.value,
                contracts.get(l.contract_id),
                cost_nodes.get(l.cost_node_id),
                cost_types.get(l.cost_type_id),
            ])

        return ws

    def _write_buyers(self, wb: Workbook, buyers) -> Worksheet:
        ws = wb.create_sheet("DICTS_BUYERS")
        ws.append(["tax_number","name","id" ])

        for c in buyers:
            ws.append([c.tax_number,c.name,str(c.id)  ])

        return ws

    def _write_sellers(self, wb: Workbook, sellers) -> Worksheet:
        ws = wb.create_sheet("DICTS_SELLERS")
        ws.append(["tax_number","name","id" ])

        for c in sellers:
            ws.append([c.tax_number,c.name,str(c.id)  ])

        return ws

    def _write_tax_treatment(self, wb: Workbook, tax_treatments) -> Worksheet:
        ws = wb.create_sheet("DICTS_TAX_TREATMENTS")
        ws.append(["value","key" ])

        for k,v in tax_treatments.items():
            ws.append([v,k])

        return ws

    def _write_contracts(self, wb: Workbook, contracts) -> Worksheet:
        ws = wb.create_sheet("DICTS_CONTRACTS")
        ws.append(["code",  "name","id"])

        for c in contracts:
            ws.append([c.code, c.name ,str(c.id)])

        return ws

    def _write_cost_nodes(self, wb: Workbook, cost_nodes) -> Worksheet:
        ws = wb.create_sheet("DICTS_COST_NODES")
        ws.append([
            "code",
            "name",
            "budget",
            "id",
            "contract_id",
            "parent_id"
        ])

        for n in cost_nodes:
            ws.append([
                n.code,
                n.name,
                n.budget,
                str(n.id),
                str(n.contract_id),
                str(n.parent_id) if n.parent_id else None
            ])

        return ws

    def _write_cost_types(self, wb: Workbook, cost_types) -> Worksheet:
        ws = wb.create_sheet("DICTS_COST_TYPES")
        ws.append(["code", "name","id"])

        for ct in cost_types:
            ws.append([ ct.code, ct.name,str(ct.id)])

        return ws

    def _apply_dropdowns(
        self,
        *,
        invoices_ws:Worksheet,
        lines_ws: Worksheet,
        buyers_ws: Worksheet,
        sellers_ws: Worksheet,
        contracts_ws: Worksheet,
        cost_nodes_ws: Worksheet,
        cost_types_ws: Worksheet,
        tax_treatments_ws: Worksheet,
    ) -> None:

        max_rows = 2000  # bezpieczny limit

        # --- company ---
        buyers_range = f"DICTS_BUYERS!$A$2:$A${buyers_ws.max_row}"
        dv_buyers = DataValidation(
            type="list",
            formula1=f"={buyers_range}",
            allow_blank=True,
        )
        invoices_ws.add_data_validation(dv_buyers)
        dv_buyers.add(f"D2:D{max_rows}")  # contract_id column

        sellers_range = f"DICTS_SELLERS!$A$2:$A${sellers_ws.max_row}"
        dv_sellers = DataValidation(
            type="list",
            formula1=f"={sellers_range}",
            allow_blank=True,
        )
        invoices_ws.add_data_validation(dv_sellers)
        dv_sellers.add(f"E2:E{max_rows}")  # contract_id column

        # --- CONTRACT ---
        contract_range = f"DICTS_CONTRACTS!$A$2:$A${contracts_ws.max_row}"
        dv_contract = DataValidation(
            type="list",
            formula1=f"={contract_range}",
            allow_blank=True,
        )
        lines_ws.add_data_validation(dv_contract)
        dv_contract.add(f"J2:J{max_rows}")  # contract_id column

        # --- COST NODE ---
        cost_node_range = f"DICTS_COST_NODES!$A$2:$A${cost_nodes_ws.max_row}"
        dv_cost_node = DataValidation(
            type="list",
            formula1=f"={cost_node_range}",
            allow_blank=True,
        )
        lines_ws.add_data_validation(dv_cost_node)
        dv_cost_node.add(f"K2:K{max_rows}")

        # --- COST TYPE ---
        cost_type_range = f"DICTS_COST_TYPES!$A$2:$A${cost_types_ws.max_row}"
        dv_cost_type = DataValidation(
            type="list",
            formula1=f"={cost_type_range}",
            allow_blank=True,
        )
        lines_ws.add_data_validation(dv_cost_type)
        dv_cost_type.add(f"L2:L{max_rows}")

        tax_treatment_range = f"DICTS_TAX_TREATMENTS!$A$2:$A${tax_treatments_ws.max_row}"
        dv_tax_treatment = DataValidation(
            type="list",
            formula1=f"={tax_treatment_range}",
            allow_blank=True,
        )
        lines_ws.add_data_validation(dv_tax_treatment)
        dv_tax_treatment.add(f"I2:I{max_rows}")






