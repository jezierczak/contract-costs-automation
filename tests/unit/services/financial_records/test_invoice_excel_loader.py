from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pandas as pd
import pytest

import contract_costs.config as cfg
from contract_costs.model.amount import VatRate
from contract_costs.model.financial_record import PaymentMethod
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.financial_records.assigment.invoice_sources.excel.invoice_excel_loader import (
    _parse_vat_rate,
    load_invoice_excel_batch,
)


def test_parse_vat_rate_maps_enum_name() -> None:
    assert _parse_vat_rate("vat_23") == VatRate.VAT_23


def test_parse_vat_rate_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        _parse_vat_rate("vat_99")


def test_load_invoice_excel_batch_parses_happy_path(monkeypatch) -> None:
    invoice_id = uuid4()
    line_id = uuid4()
    company_id = uuid4()

    df_invoices = pd.DataFrame(
        [
            {
                "action": "APPLY",
                "invoice_number": "FV/1/2026",
                "invoice_id": str(invoice_id),
                "old_invoice_number": None,
                "invoice_date": date(2026, 2, 17),
                "selling_date": date(2026, 2, 17),
                "buyer_NIP": "676-268-01-95",
                "seller_NIP": "6792740424",
                "payment_method": "cash",
                "due_date": date(2026, 2, 20),
                "paid_date": None,
                "payment_status": "unknown",
                "tags": "a,b",
            }
        ]
    )
    df_lines = pd.DataFrame(
        [
            {
                "id": str(line_id),
                "record_reference": "FV/1/2026",
                "item_name": "Item 1",
                "description": "Desc",
                "quantity": "2",
                "unit": "szt",
                "amount": "100.00",
                "amount_type": "net",
                "vat_rate": "VAT_23",
                "tax_treatment": "tax_deductible",
                "contract_code": "C-1",
                "contract_node_code": "CN-1",
                "value_type_code": "VT-1",
                "agreement_code": None,
                "agreement_node_code": None,
            }
        ]
    )
    df_buyers = pd.DataFrame([{"id": company_id, "name": "Buyer", "tax_number": "6762680195"}])
    df_sellers = pd.DataFrame([{"id": company_id, "name": "Seller", "tax_number": "6792740424"}])

    def _fake_read_excel(path, sheet_name):
        _ = path
        mapping = {
            cfg.FINANCIAL_RECORD_METADATA_SHEET_NAME: df_invoices,
            cfg.FINANCIAL_RECORD_ITEMS_SHEET_NAME: df_lines,
            cfg.DICTS_BUYERS: df_buyers,
            cfg.DICTS_SELLERS: df_sellers,
        }
        return mapping[sheet_name]

    monkeypatch.setattr(pd, "read_excel", _fake_read_excel)

    batch = load_invoice_excel_batch(Path("dummy.xlsx"))

    assert len(batch.financial_records) == 1
    assert len(batch.lines) == 1
    assert len(batch.buyers) == 1
    assert len(batch.sellers) == 1
    assert batch.financial_records[0].reference == "FV/1/2026"
    assert batch.financial_records[0].payment_method == PaymentMethod.CASH
    assert batch.lines[0].unit == UnitOfMeasure.PIECE
    assert batch.lines[0].amount.value == Decimal("100.00")


def test_load_invoice_excel_batch_rejects_empty_invoice_number(monkeypatch) -> None:
    df_invoices = pd.DataFrame([{"invoice_number": "   "}])
    df_lines = pd.DataFrame([{"item_name": "Item"}])
    df_companies = pd.DataFrame([{"id": uuid4(), "name": "X", "tax_number": "1"}])

    def _fake_read_excel(path, sheet_name):
        _ = path
        mapping = {
            cfg.FINANCIAL_RECORD_METADATA_SHEET_NAME: df_invoices,
            cfg.FINANCIAL_RECORD_ITEMS_SHEET_NAME: df_lines,
            cfg.DICTS_BUYERS: df_companies,
            cfg.DICTS_SELLERS: df_companies,
        }
        return mapping[sheet_name]

    monkeypatch.setattr(pd, "read_excel", _fake_read_excel)

    with pytest.raises(ValueError, match="empty invoice_number"):
        load_invoice_excel_batch(Path("dummy.xlsx"))
