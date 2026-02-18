import re
from enum import Enum
from uuid import UUID

from openpyxl import Workbook
from openpyxl.workbook.defined_name import DefinedName

from openpyxl.worksheet.worksheet import Worksheet

from contract_costs.infrastructure.excel.excel_common_methods import ExcelCommonMethods
from contract_costs.model.amount import AmountInputType
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.financial_records.assigment.prepare.dto.assignment_export_bundle import FinancialRecordAssignmentExportBundle
from contract_costs.services.financial_records.assigment.prepare.export.invoice_assignment_exporter import InvoiceAssignmentExporter

import contract_costs.config as cfg
from pathlib import Path

work_dir = cfg.WORK_DIR.resolve().as_posix()

class ExcelInvoiceAssignmentExporter(InvoiceAssignmentExporter):

    def export(
            self,
            *,
            organization_id: UUID,
            bundle: FinancialRecordAssignmentExportBundle,
            output_path: Path
    ) -> None:
        wb = Workbook()

        invoices_ws = self._write_invoices(wb, bundle.records, organization_id)
        lines_ws = self._write_invoice_lines(wb, bundle.record_lines)

        buyers_ws = self._write_buyers(wb, bundle.buyers)
        sellers_ws = self._write_sellers(wb, bundle.sellers)

        project_contracts_ws = self._write_contracts(
            wb, bundle.project_contracts, cfg.DICTS_PROJECT_CONTRACTS
        )
        project_nodes_ws = self._write_cost_nodes(
            wb, bundle.project_contract_nodes, cfg.DICTS_PROJECT_COST_NODES
        )
        agreement_contracts_ws = self._write_contracts(
            wb, bundle.agreement_contracts, cfg.DICTS_AGREEMENT_CONTRACTS
        )
        agreement_nodes_ws = self._write_cost_nodes(
            wb, bundle.agreement_contract_nodes, cfg.DICTS_AGREEMENT_COST_NODES
        )

        cost_types_ws = self._write_value_types(wb, bundle.value_types)

        amount_input_type_ws = self._write_dictionary(
            wb, bundle.amount_input_types, cfg.DICTS_AMOUNT_INPUT_TYPES
        )

        tax_treatment_ws = self._write_dictionary(
            wb, bundle.amount_types, cfg.DICTS_TAX_TREATMENTS
        )

        payment_method_ws = self._write_dictionary(
            wb, bundle.payment_methods, cfg.DICTS_PAYMENT_METHODS
        )

        payment_status_ws = self._write_dictionary(
            wb, bundle.payment_status, cfg.DICTS_PAYMENT_STATUS
        )

        units_ws = self._write_dictionary(
            wb, bundle.units, cfg.DICTS_UNITS
        )

        vat_rates_ws = self._write_dictionary(
            wb, bundle.vat_rates, cfg.DICTS_VAT_RATES
        )

        actions_ws = self._write_dictionary(
            wb, bundle.actions, cfg.DICTS_ACTIONS
        )

        # Named ranges
        self._define_named_ranges(wb, project_nodes_ws)
        self._define_named_ranges(wb, agreement_nodes_ws)

        self._apply_dropdowns(
            invoices_ws=invoices_ws,
            lines_ws=lines_ws,
            buyers_ws=buyers_ws,
            sellers_ws=sellers_ws,
            project_contracts_ws=project_contracts_ws,
            agreement_contracts_ws=agreement_contracts_ws,
            cost_types_ws=cost_types_ws,
            amount_input_type_ws=amount_input_type_ws,
            tax_treatments_ws=tax_treatment_ws,
            payment_method_ws=payment_method_ws,
            payment_status_ws=payment_status_ws,
            units_ws=units_ws,
            vat_rates_ws=vat_rates_ws,
            actions_ws=actions_ws,
        )

        DATA_SHEETS = {
            cfg.FINANCIAL_RECORD_METADATA_SHEET_NAME,
            cfg.FINANCIAL_RECORD_ITEMS_SHEET_NAME,
        }

        for ws in wb.worksheets:
            ExcelCommonMethods.style_header(ws)
            ExcelCommonMethods.autosize_columns(ws)

            if ws.title in DATA_SHEETS:
                ExcelCommonMethods.freeze_header(ws)
                ExcelCommonMethods.apply_autofilter(ws)
                ExcelCommonMethods.zebra_rows(ws)

        # opcjonalnie: usuń domyślny pusty sheet
        if "Sheet" in wb.sheetnames:
            del wb["Sheet"]

        wb.save(output_path)

    @staticmethod
    def _write_invoices(wb: Workbook, invoices,organization_id: UUID) -> Worksheet:
        ws = wb.create_sheet(cfg.FINANCIAL_RECORD_METADATA_SHEET_NAME)

        headers = [
            "action",  # APPLY | MODIFY | DELETE
            "invoice_number",  # nowy numer (lub pusty → generator)
            "invoice_id",
            "old_invoice_number",  # 🔒 UKRYTA – tylko dla MODIFY
            "invoice_date",
            "selling_date",
            "buyer_NIP",
            "seller_NIP",
            "payment_method",
            "payment_status",
            "due_date",
            "paid_date",
            "tags",
            "timestamp",
            "scan_filename",
            "scan_link",
            "scan_folder",
        ]
        ws.append(headers)



        for i in invoices:
            scan_rel = i.primary_document_path
            abs_path = (
                (Path(work_dir)/ str(organization_id) / scan_rel).resolve().as_posix()
                if scan_rel
                else None
            )
            scan_link = (
                f'=HYPERLINK("file:///{abs_path}", "📄 Otwórz")'
                if scan_rel else None
            )

            scan_folder = (
                f'=HYPERLINK("file:///{work_dir}/{str(organization_id)}/{Path(scan_rel).parent.as_posix()}", "📂 Folder")'
                if scan_rel else None
            )

            ws.append([
                str(InvoiceCommand.APPLY.value),
                i.reference,
                i.record_id,
                i.reference,  # old_invoice_number
                i.invoice_date,
                i.selling_date,
                str(i.buyer_tax_number) if i.buyer_tax_number else None,
                str(i.seller_tax_number) if i.seller_tax_number else None,
                i.payment_method.value if i.payment_method else None,
                i.payment_status.value if i.payment_status else None,
                i.due_date,
                i.paid_date,
                ",".join(sorted(i.tags)) if i.tags else None,
                i.timestamp,
                scan_rel,
                scan_link,
                scan_folder
            ])
        ws.column_dimensions["C"].hidden = True
        ws.column_dimensions["D"].hidden = True
        ws.column_dimensions["O"].hidden = True  # scan_filename
        return ws
    @staticmethod
    def _write_invoice_lines( wb: Workbook, lines) -> Worksheet:
        ws = wb.create_sheet(cfg.FINANCIAL_RECORD_ITEMS_SHEET_NAME)

        headers = [
            "id",
            "record_reference",
            "item_name",
            "description",
            "quantity",
            "unit",
            "amount",
            "vat_rate",
            "amount_type",
            "tax_treatment",
            "contract_code",
            "contract_node_code",
            "value_type_code",
            "agreement_code",
            "agreement_node_code"
        ]
        ws.append(headers)

        for l in lines:
            ws.append([
                str(l.id),
                l.record_reference,
                l.item_name,
                l.description,
                l.quantity,
                l.unit.value if l.unit else None,
                l.net,
                l.vat_rate.name if isinstance(l.vat_rate, Enum) else l.vat_rate,
                AmountInputType.NET.value,
                l.tax_treatment.value,
                l.contract_code,
                l.contract_node_code,
                l.value_type_code,
                l.agreement_code,
                l.agreement_node_code,
            ])

        ws.column_dimensions["A"].hidden = True
        return ws

    def _write_buyers(self, wb: Workbook, buyers) -> Worksheet:
        ws = wb.create_sheet(cfg.DICTS_BUYERS)
        ws.append(["tax_number","name","id" ])

        for c in buyers:
            ws.append([c.tax_number,c.name,str(c.id)  ])
        ws.column_dimensions["C"].hidden = True
        return ws

    @staticmethod
    def _write_sellers(wb: Workbook, sellers) -> Worksheet:
        ws = wb.create_sheet(cfg.DICTS_SELLERS)
        ws.append(["tax_number","name","id" ])

        for c in sellers:
            ws.append([c.tax_number,c.name,str(c.id)  ])
        ws.column_dimensions["C"].hidden = True
        return ws
    @staticmethod
    def _write_contracts( wb: Workbook, contracts,sheet_name: str) -> Worksheet:
        ws = wb.create_sheet(sheet_name)
        ws.append(["code",  "name","id"])

        for c in contracts:
            ws.append([c.code, c.name ,str(c.id)])
        ws.column_dimensions["C"].hidden = True
        return ws

    @staticmethod
    def _write_cost_nodes(wb: Workbook, cost_nodes,sheet_name: str) -> Worksheet:
        ws = wb.create_sheet(sheet_name)
        ws.append([
            "contract_code",
            "code",
            "name",
            "budget",
            "id",
            "contract_id",
            "parent_id"
        ])
        cost_nodes.sort(key=lambda c: (c.contract_code,c.code))

        for n in cost_nodes:

            ws.append([
                n.contract_code,
                n.code,
                n.name,
                n.budget,
                str(n.id),
                str(n.contract_code),
                str(n.parent_id) if n.parent_id else None
            ])
        ws.column_dimensions["D"].hidden = True  # id
        ws.column_dimensions["E"].hidden = True  # contract_id
        ws.column_dimensions["F"].hidden = True  # parent_id
        return ws
    @staticmethod
    def _to_excel_safe_name(name: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9_]", "_", name)
        if safe[0].isdigit():
            safe = f"X_{safe}"
        return safe

    def _define_named_ranges(
        self,
        wb: Workbook,
        cost_nodes_ws: Worksheet,
        prefix: str| None = None,
    ) -> None:

        rows = list(cost_nodes_ws.iter_rows(min_row=2, values_only=True))
        by_contract: dict[str, list[int]] = {}

        for idx, row in enumerate(rows, start=2):
            contract_code = row[0]
            if not isinstance(contract_code, str):
                continue
            by_contract.setdefault(contract_code, []).append(idx)

        for contract_code, row_numbers in by_contract.items():
            start = row_numbers[0]
            end = row_numbers[-1]
            name_prefix = prefix or ""
            name = f"{name_prefix}{self._to_excel_safe_name(contract_code)}"
            formula = f"'{cost_nodes_ws.title}'!$B${start}:$B${end}"

            wb.defined_names[name] = DefinedName(
                name=name,
                attr_text=formula,
            )

    def _write_value_types(self, wb: Workbook, cost_types) -> Worksheet:
        ws = wb.create_sheet(cfg.DICTS_COST_TYPES)
        ws.append(["code", "name","id"])

        for ct in cost_types:
            ws.append([ ct.code, ct.name,str(ct.id)])

        ws.column_dimensions["C"].hidden = True
        return ws

    @staticmethod
    def _write_dictionary( wb: Workbook, dictionary: dict[str,str],dicts_sheet_name: str) -> Worksheet:
        ws = wb.create_sheet(dicts_sheet_name)
        ws.append(["label","code" ])

        for code,label in dictionary.items():
            ws.append([label,code])

        return ws

        # ============================================================
        # DROPDOWNS
        # ============================================================
    @staticmethod
    def _apply_dropdowns(
            *,
            invoices_ws: Worksheet,
            lines_ws: Worksheet,
            buyers_ws: Worksheet,
            sellers_ws: Worksheet,
            project_contracts_ws: Worksheet,
            agreement_contracts_ws: Worksheet,
            cost_types_ws: Worksheet,
            amount_input_type_ws: Worksheet,
            tax_treatments_ws: Worksheet,
            payment_method_ws: Worksheet,
            payment_status_ws: Worksheet,
            units_ws: Worksheet,
            vat_rates_ws: Worksheet,
            actions_ws: Worksheet,
    ) -> None:

        max_rows = 2000  # bezpieczny limit

        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            actions_ws,
            cfg.DICTS_ACTIONS,
            invoices_ws,
            "A"
        )

        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            buyers_ws,
            cfg.DICTS_BUYERS,
            invoices_ws,
            "G"
        )

        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            sellers_ws,
            cfg.DICTS_SELLERS,
            invoices_ws,
            "H"
        )
        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            payment_method_ws,
            cfg.DICTS_PAYMENT_METHODS,
            invoices_ws,
            "I"
        )
        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            payment_status_ws,
            cfg.DICTS_PAYMENT_STATUS,
            invoices_ws,
            "J"
        )

        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            units_ws,
            cfg.DICTS_UNITS,
            lines_ws,
            "F"
        )


        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            vat_rates_ws,
            cfg.DICTS_VAT_RATES,
            lines_ws,
            "H",
            "B"
        )

        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            amount_input_type_ws,
            cfg.DICTS_AMOUNT_INPUT_TYPES,
            lines_ws,
            "I"
        )

        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            tax_treatments_ws,
            cfg.DICTS_TAX_TREATMENTS,
            lines_ws,
            "J"
        )

        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            project_contracts_ws,
            cfg.DICTS_PROJECT_CONTRACTS,
            lines_ws,
            "K"
        )


        ExcelCommonMethods.apply_formula_dropdown(
            source_ws=lines_ws,
            target_column="L",
            formula="=INDIRECT($K2)",
            max_rows=2000,
        )

        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            cost_types_ws,
            cfg.DICTS_COST_TYPES,
            lines_ws,
            "M"
        )
        ExcelCommonMethods.apply_one_dropdown(
            max_rows,
            agreement_contracts_ws,
            cfg.DICTS_AGREEMENT_CONTRACTS,
            lines_ws,
            "N"
        )

        ExcelCommonMethods.apply_formula_dropdown(
            source_ws=lines_ws,
            target_column="O",
            formula="=INDIRECT($N2)",
            max_rows=2000,
        )

