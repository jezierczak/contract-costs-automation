import pytest
from contract_costs.model.amount import VatRate
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.ai_invoice_mapper import AIDocumentMapper


@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("23", VatRate.VAT_23),
        ("23%", VatRate.VAT_23),
        ("0.23", VatRate.VAT_23),
        ("8", VatRate.VAT_8),
        ("0.08", VatRate.VAT_8),
        ("5", VatRate.VAT_5),
        ("0", VatRate.VAT_0),
        ("zw", VatRate.VAT_ZW),
        ("zw.", VatRate.VAT_ZW),
        ("zwolnione", VatRate.VAT_ZW),
        (None, VatRate.VAT_23),
        ("cos dziwnego", VatRate.VAT_23),
    ],
)
def test_parse_vat(input_value, expected):
    result = AIDocumentMapper._parse_vat(input_value)
    assert result == expected