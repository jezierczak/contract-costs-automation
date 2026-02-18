from contract_costs.model.document import DocumentType
from contract_costs.services.documents.document_selector import DocumentSelector
from tests.builders.document_builder import DocumentBuilder


def test_resolve_primary_returns_invoice_when_present():
    first = DocumentBuilder().with_document_type(DocumentType.OTHER).build()
    invoice = DocumentBuilder().with_document_type(DocumentType.INVOICE).build()
    docs = [first, invoice]

    result = DocumentSelector.resolve_primary(docs)

    assert result == invoice


def test_resolve_primary_returns_first_when_no_invoice():
    first = DocumentBuilder().with_document_type(DocumentType.OTHER).build()
    second = DocumentBuilder().with_document_type(DocumentType.RECEIPT).build()

    result = DocumentSelector.resolve_primary([first, second])

    assert result == first


def test_resolve_primary_path_returns_none_for_empty():
    assert DocumentSelector.resolve_primary_path([]) is None
