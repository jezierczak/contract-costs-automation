from contract_costs.model.document import DocumentType
from tests.builders.document_builder import DocumentBuilder


def test_document_creation():
    doc = DocumentBuilder().build()

    assert doc.filename == "test.pdf"
    assert doc.document_type is None
    assert doc.file_hash == "abc123"

def test_with_document_type_returns_new_instance():
    doc = DocumentBuilder().build()

    updated = doc.with_document_type(DocumentType.INVOICE)

    assert updated.document_type == DocumentType.INVOICE
    assert doc.document_type is None
    assert updated is not doc


def test_with_document_number_returns_new_instance():
    doc = DocumentBuilder().build()

    updated = doc.with_document_number("FV/01/2025")

    assert updated.document_number == "FV/01/2025"
    assert doc.document_number is None


def test_document_replace_chain():
    doc = DocumentBuilder().build()

    updated = (
        doc
        .with_document_type(DocumentType.INVOICE)
        .with_document_number("FV/01")
        .with_seller_nip("1234567890")
    )

    assert updated.document_type == DocumentType.INVOICE
    assert updated.document_number == "FV/01"
    assert updated.seller_nip == "1234567890"

    # oryginał bez zmian
    assert doc.document_type is None

import pytest

def test_document_disallows_dynamic_attributes():
    doc = DocumentBuilder().build()

    with pytest.raises(AttributeError):
        doc.some_random_field = "boom"
