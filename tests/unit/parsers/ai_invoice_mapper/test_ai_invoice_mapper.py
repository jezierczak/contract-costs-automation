from decimal import Decimal

import pytest

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.ai_invoice_mapper import \
    AIDocumentMapper


def test_map_minimal_invoice():
    mapper = AIDocumentMapper()

    data = {
        "document_type": "invoice",
        "invoice_number": "FV/1/2026",
        "invoice_date": "2026-01-10",
        "payment_method": "transfer",
        "payment_status": "unpaid",
        "invoice_items": [
            {
                "item_name": "Roboty ziemne",
                "quantity": "10",
                "unit": "m3",
                "net_total": "1000",
                "vat_rate": "23",
            }
        ],
        "buyer_name": "ABC Sp z o.o.",
        "buyer_tax_number": "123-456-78-90",
        "seller_name": "Jan Kowalski",
        "seller_tax_number": "987-654-32-10",
    }

    result = mapper.map(data)

    assert result.document_type.value == "invoice"
    assert result.record.reference == "FV/1/2026"
    assert len(result.lines) == 1

    line = result.lines[0]

    assert line.quantity == Decimal("10")
    assert line.unit.name == "CUBIC_METER"
    assert line.amount.value == Decimal("1000")
    assert line.amount.vat_rate.name == "VAT_23"

    assert result.buyer.name == "ABC Sp z o.o."
    assert result.seller.name == "Jan Kowalski"

def test_generates_invoice_number_when_missing():
    mapper = AIDocumentMapper()

    data = {
        "document_type": "invoice",
        "invoice_items": [],
    }

    result = mapper.map(data)

    assert result.record.reference.startswith("AI-")
    assert len(result.record.reference) > 5


def test_mapper_handles_garbage_data():
    mapper = AIDocumentMapper()

    data = {
        "document_type": "???",
        "invoice_number": "",
        "invoice_date": "32-13-2026",
        "invoice_items": [
            {
                "item_name": None,
                "quantity": "abc",
                "unit": "???",
                "net_total": "xyz",
                "vat_rate": "???",
            }
        ],
    }

    result = mapper.map(data)

    assert result.document_type.name == "UNKNOWN"
    assert result.lines[0].quantity == Decimal("0")
    assert result.lines[0].unit.name == "UNKNOWN"
    assert result.lines[0].amount.value == Decimal("0")


@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("1234.56", Decimal("1234.56")),
        ("1234,56", Decimal("1234.56")),
        ("1 234,56", Decimal("1234.56")),
        ("1,234.56", Decimal("1234.56")),
    ],
)
def test_parse_decimal_formats(input_value, expected):
    result = AIDocumentMapper._parse_decimal(input_value)
    assert result == expected