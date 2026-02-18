import pytest
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.ai_invoice_mapper import AIDocumentMapper


@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("szt", UnitOfMeasure.PIECE),
        ("szt.", UnitOfMeasure.PIECE),
        ("Szt.", UnitOfMeasure.PIECE),
        ("m", UnitOfMeasure.METER),
        ("m2", UnitOfMeasure.SQUARE_METER),
        ("m²", UnitOfMeasure.SQUARE_METER),
        ("m3", UnitOfMeasure.CUBIC_METER),
        ("kg", UnitOfMeasure.KILOGRAM),
        ("godz", UnitOfMeasure.HOUR),
        ("usługa", UnitOfMeasure.SERVICE),
        ("cos", UnitOfMeasure.UNKNOWN),
        (None, UnitOfMeasure.UNKNOWN),
    ],
)
def test_parse_unit(input_value, expected):
    result = AIDocumentMapper._parse_unit(input_value)
    assert result == expected