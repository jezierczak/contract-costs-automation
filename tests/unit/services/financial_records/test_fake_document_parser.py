from pathlib import Path

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.fake_invoice_parser import (
    FakeDocumentParser,
)


def test_fake_document_parser_returns_document_parse_result_contract() -> None:
    parser = FakeDocumentParser()
    result = parser.parse(Path("dummy.pdf"))

    assert result.document_type.value in {"invoice", "proforma", "receipt"}
    assert result.record.reference
    assert result.lines is not None
