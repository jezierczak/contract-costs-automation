from pathlib import Path
from uuid import UUID
from decimal import Decimal
from datetime import datetime

import contract_costs.config as cfg

import pandas as pd

from contract_costs.services.invoices.dto.common import (
    InvoiceExcelBatch,
    InvoiceUpdate,
    InvoiceLineUpdate,
)
from contract_costs.model.invoice import InvoiceStatus, PaymentStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.amount import Amount, VatRate, TaxTreatment
from contract_costs.model.invoice import PaymentMethod


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
    if value is None:
        raise ValueError("vat_rate is required")

    # pandas może dać float albo str
    if isinstance(value, float):
        dec = Decimal(str(value))
    else:
        dec = Decimal(str(value).replace(",", "."))

    return VatRate(dec)

def load_invoice_excel_batch(path: Path) -> InvoiceExcelBatch:
    df_invoices = pd.read_excel(path, sheet_name=cfg.INVOICE_METADATA_SHEET_NAME)
    df_lines = pd.read_excel(path, sheet_name=cfg.INVOICE_ITEMS_SHEET_NAME)

    invoices: list[InvoiceUpdate] = []
    for _, row in df_invoices.iterrows():
        invoices.append(
            InvoiceUpdate(
                id= row["invoice_number"],
                invoice_number=str(row["invoice_number"]),
                invoice_date=_parse_date(row["invoice_date"]),
                selling_date=_parse_date(row["selling_date"]),
                buyer_id=row["buyer_NIP"],
                seller_id=row["seller_NIP"],
                payment_method=PaymentMethod(row["payment_method"])
                if not pd.isna(row["payment_method"])
                else None,
                due_date=_parse_date(row["due_date"]),
                payment_status=PaymentStatus(row["payment_status"])
                if not pd.isna(row["payment_status"])
                else None,
                status=InvoiceStatus.PROCESSED
            )
        )

    lines: list[InvoiceLineUpdate] = []
    for _, row in df_lines.iterrows():
        lines.append(
            InvoiceLineUpdate(
                invoice_line_id=_parse_uuid(normalize(row["invoice_line_id"])),
                invoice_id=str(row["invoice_number"])
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
                contract_id=normalize(row.get("contract_id")),  # <-- CODE
                cost_node_id=normalize(row.get("cost_node_id")),  # <-- CODE
                cost_type_id=normalize(row.get("cost_type_id")),  # <-- CODE
            )
        )

    return InvoiceExcelBatch(
        invoices=invoices,
        lines=lines,
    )


