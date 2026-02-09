from pathlib import Path
from uuid import UUID
from decimal import Decimal
from datetime import datetime

import contract_costs.config as cfg

import pandas as pd

from contract_costs.services.common.resolve_utils import normalize_tax_number
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    InvoiceExcelBatch,
    FinancialRecordUpdate,
    FinancialRecordLineUpdate,
)
from contract_costs.model.financial_record import FinancialRecordStatus, PaymentStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.amount import Amount, VatRate, TaxTreatment, AmountInputType
from contract_costs.model.financial_record import PaymentMethod
from contract_costs.services.financial_records.assigment.prepare.dto.company_export import CompanyExport


def _parse_uuid(value):
    if pd.isna(value):
        return None
    return UUID(str(value))


def _parse_date(value):
    if pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    return datetime.fromisoformat(str(value)).date()

def normalize(value):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    return value

def _parse_vat_rate(value) -> VatRate:
    if not value:
        raise ValueError("vat_rate is required")

    try:
        return VatRate[value.strip().upper()]
    except KeyError:
        raise ValueError(f"Invalid vat_rate: {value}")


def load_invoice_excel_batch(path: Path) -> InvoiceExcelBatch:
    df_invoices = pd.read_excel(path, sheet_name=cfg.FINANCIAL_RECORD_METADATA_SHEET_NAME)
    df_lines = pd.read_excel(path, sheet_name=cfg.FINANCIAL_RECORD_ITEMS_SHEET_NAME)
    df_buyers = pd.read_excel(path, sheet_name=cfg.DICTS_BUYERS)
    df_sellers = pd.read_excel(path, sheet_name=cfg.DICTS_SELLERS)

    df_invoices = df_invoices.dropna(how="all")

    col = df_invoices["invoice_number"]

    invalid_mask = col.isna() | (col.astype(str).str.strip() == "")

    if invalid_mask.any():
        bad_rows = list(invalid_mask[invalid_mask].index + 1)  # +1 = numer wiersza dla usera
        raise ValueError(
            f"Invoice sheet contains empty invoice_number in rows: {bad_rows}. "
            "Please fill all invoice numbers."
        )

    df_invoices = df_invoices.reset_index(drop=True)

    col = df_lines["item_name"]

    invalid_mask = col.isna() | (col.astype(str).str.strip() == "")

    if invalid_mask.any():
        bad_rows = list(invalid_mask[invalid_mask].index + 1)
        raise ValueError(
            f"[{cfg.FINANCIAL_RECORD_METADATA_SHEET_NAME}] "
            f"Empty invoice_number in rows: {bad_rows}. "
            "Please fill all invoice numbers."
        )

    df_lines = df_lines.reset_index(drop=True)


    invoices: list[FinancialRecordUpdate] = []
    for _, row in df_invoices.iterrows():

        invoices.append(
            FinancialRecordUpdate(
                command=InvoiceCommand(str(row["action"])) if not pd.isna(row["action"]) else InvoiceCommand.APPLY,
                reference=str(row["invoice_number"]) ,
                record_id=_parse_uuid(normalize(row["invoice_id"])),
                old_reference=str(row["old_invoice_number"]) if not pd.isna(row["old_invoice_number"]) else None,
                invoice_date=_parse_date(row["invoice_date"]),
                selling_date=_parse_date(row["selling_date"]),
                buyer_tax_number=normalize_tax_number(row["buyer_NIP"]),
                seller_tax_number=normalize_tax_number(row["seller_NIP"]) if not pd.isna(row["seller_NIP"]) else None,
                payment_method=PaymentMethod(row["payment_method"])
                if not pd.isna(row["payment_method"])
                else PaymentMethod.UNKNOWN,
                due_date=_parse_date(row["due_date"]),
                paid_date=_parse_date(row["paid_date"]),
                payment_status=PaymentStatus(row["payment_status"])
                if not pd.isna(row["payment_status"])
                else PaymentStatus.UNKNOWN,
                status=FinancialRecordStatus.IN_PROGRESS, ## OR PROCESSED
                tags = str(row["tags"]) if not pd.isna(row["tags"]) else None,
                # scan_filename= str(row["scan_filename"]) if not pd.isna(row["scan_filename"]) else None,
            )
        )

    lines: list[FinancialRecordLineUpdate] = []
    for _, row in df_lines.iterrows():
        lines.append(
            FinancialRecordLineUpdate(
                record_line_id=_parse_uuid(normalize(row["id"])),
                record_reference=str(row["invoice_number"])
                if not pd.isna(row["invoice_number"])
                else None,
                item_name=normalize(row["item_name"]),
                description=normalize(row.get("description")),
                quantity=Decimal(str(row["quantity"])),
                unit=normalize(UnitOfMeasure(row["unit"])),
                # amount=Amount(
                #     value=Decimal(str(row["net"])),
                #     vat_rate=_parse_vat_rate(row["vat_rate"])
                #     if not pd.isna(row["vat_rate"])
                #     else VatRate.VAT_ZW,
                #     tax_treatment=TaxTreatment(row["tax_treatment"]),
                # ),
                amount=Amount.from_input(
                    value=Decimal(str(row["amount"])),  # <- fizyczna liczba z Excela
                    input_type=(
                        AmountInputType(row["amount_type"])
                        if not pd.isna(row["amount_type"])
                        else AmountInputType.NET
                    ),
                    vat_rate=(
                        _parse_vat_rate(row["vat_rate"])
                        if not pd.isna(row["vat_rate"])
                        else VatRate.VAT_ZW
                    ),
                    tax_treatment=TaxTreatment(row["tax_treatment"])
                ),
                contract_id=normalize(row.get("contract_code")),  # <-- CODE
                contract_node_id=normalize(row.get("cost_node_code")),  # <-- CODE
                value_type_code=normalize(row.get("cost_type_code")),  # <-- CODE
            )
        )

    buyers: list[CompanyExport] = []
    for _, row in df_buyers.iterrows():
        buyers.append(
            CompanyExport(
                id = row["id"],
                name = row["name"],
                tax_number =row["tax_number"]
            )
        )
    sellers: list[CompanyExport] = []
    for _, row in df_sellers.iterrows():
        sellers.append(
            CompanyExport(
                id = row["id"],
                name = row["name"],
                tax_number =row["tax_number"]
            )
        )

    return InvoiceExcelBatch(
        financial_records=invoices,
        lines=lines,
        buyers=buyers,
        sellers=sellers
    )


