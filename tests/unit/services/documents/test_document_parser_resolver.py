import pytest
from unittest.mock import MagicMock

from contract_costs.model.document import DocumentSource
from contract_costs.services.documents.process.document_parser_resolver import (
    DefaultDocumentParserResolver,
)


def test_resolver_returns_ksef_parser_for_ksef_source():
    pdf_parser = MagicMock()
    ksef_parser = MagicMock()
    image_parser = MagicMock()

    resolver = DefaultDocumentParserResolver(
        pdf_parser=pdf_parser,
        ksef_parser=ksef_parser,
        image_parser=image_parser,
    )

    assert resolver.resolve(DocumentSource.KSEF) is ksef_parser


def test_resolver_raises_for_unsupported_source():
    resolver = DefaultDocumentParserResolver(
        pdf_parser=MagicMock(),
        ksef_parser=MagicMock(),
        image_parser=MagicMock(),
    )

    with pytest.raises(ValueError, match="No parser registered"):
        resolver.resolve(DocumentSource.OTHER)
