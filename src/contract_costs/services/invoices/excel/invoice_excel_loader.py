from pathlib import Path
from uuid import UUID
from decimal import Decimal
from datetime import datetime

import contract_costs.config as cfg

import pandas as pd

from contract_costs.services.common.resolve_utils import normalize_tax_number
from contract_costs.services.invoices.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.dto.common import (
    InvoiceExcelBatch,
    InvoiceUpdate,
    InvoiceLineUpdate,
)
from contract_costs.model.invoice import InvoiceStatus, PaymentStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.amount import Amount, VatRate, TaxTreatment
from contract_costs.model.invoice import PaymentMethod
from contract_costs.services.invoices.dto.export.company_export import CompanyExport


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
    df_invoices = pd.read_excel(path, sheet_name=cfg.INVOICE_METADATA_SHEET_NAME)
    df_lines = pd.read_excel(path, sheet_name=cfg.INVOICE_ITEMS_SHEET_NAME)
    df_buyers = pd.read_excel(path, sheet_name=cfg.DICTS_BUYERS)
    df_sellers = pd.read_excel(path, sheet_name=cfg.DICTS_SELLERS)

    df_invoices = df_invoices.dropna(how="all")

    # 2. tylko logiczne faktury
    df_invoices = df_invoices[df_invoices["invoice_number"].notna()]
    df_invoices = df_invoices[df_invoices["invoice_number"].astype(str).str.strip() != ""]

    # 3. odetnij wszystko po pierwszej dziurze
    df_invoices = df_invoices.reset_index(drop=True)
    mask = df_invoices["invoice_number"].notna()
    if not mask.all():
        raise ValueError(
            "Invoice sheet contains empty rows between invoices. "
            "Please remove empty rows."
        )

    df_lines = df_lines.dropna(how="all")
    df_lines = df_lines[df_lines["item_name"].notna()]
    df_lines = df_lines[df_lines["item_name"].astype(str).str.strip() != ""]

    # 3. odetnij wszystko po pierwszej dziurze
    df_lines = df_lines.reset_index(drop=True)
    mask = df_lines["item_name"].notna()
    if not mask.all():
        raise ValueError(
            "Invoice Line sheet contains empty rows between lines. "
            "Please remove empty rows."
        )

    invoices: list[InvoiceUpdate] = []
    for _, row in df_invoices.iterrows():

        invoices.append(
            InvoiceUpdate(
                command=InvoiceCommand(str(row["action"])) if not pd.isna(row["action"]) else InvoiceCommand.APPLY,
                invoice_number=str(row["invoice_number"]) if not pd.isna(row["invoice_number"]) else None,
                old_invoice_number=str(row["old_invoice_number"]) if not pd.isna(row["old_invoice_number"]) else None,
                invoice_date=_parse_date(row["invoice_date"]),
                selling_date=_parse_date(row["selling_date"]),
                buyer_tax_number=normalize_tax_number(row["buyer_NIP"]),
                seller_tax_number=normalize_tax_number(row["seller_NIP"]) if not pd.isna(row["seller_NIP"]) else None,
                payment_method=PaymentMethod(row["payment_method"])
                if not pd.isna(row["payment_method"])
                else PaymentMethod.CASH,
                due_date=_parse_date(row["due_date"]),
                payment_status=PaymentStatus(row["payment_status"])
                if not pd.isna(row["payment_status"])
                else PaymentStatus.PAID,
                status=InvoiceStatus.IN_PROGRESS, ## OR PROCESSED
            )
        )

    lines: list[InvoiceLineUpdate] = []
    for _, row in df_lines.iterrows():
        lines.append(
            InvoiceLineUpdate(
                invoice_line_id=_parse_uuid(normalize(row["id"])),
                invoice_number=str(row["invoice_number"])
                if not pd.isna(row["invoice_number"])
                else None,
                item_name=normalize(row["item_name"]),
                description=normalize(row.get("description")),
                quantity=Decimal(str(row["quantity"])),
                unit=normalize(UnitOfMeasure(row["unit"])),
                amount=Amount(
                    value=Decimal(str(row["net"])),
                    vat_rate=_parse_vat_rate(row["vat_rate"])
                    if not pd.isna(row["vat_rate"])
                    else VatRate.VAT_ZW,
                    tax_treatment=TaxTreatment(row["tax_treatment"]),
                ),
                contract_id=normalize(row.get("contract_code")),  # <-- CODE
                cost_node_id=normalize(row.get("cost_node_code")),  # <-- CODE
                cost_type_id=normalize(row.get("cost_type_code")),  # <-- CODE
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
        invoices=invoices,
        lines=lines,
        buyers=buyers,
        sellers=sellers
    )


