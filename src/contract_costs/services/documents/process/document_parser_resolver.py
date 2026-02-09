from abc import ABC,abstractmethod



from contract_costs.model.document import DocumentSource
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.document_parser import \
    DocumentParser


class DocumentParserResolver(ABC):

    @abstractmethod
    def resolve(self, source: DocumentSource) -> DocumentParser:
        ...


class DefaultDocumentParserResolver(DocumentParserResolver):

    def __init__(
        self,
        pdf_parser: DocumentParser,
        ksef_parser: DocumentParser,
        image_parser: DocumentParser,
    ):
        self._pdf = pdf_parser
        self._ksef = ksef_parser
        self._image = image_parser

    def resolve(self, source: DocumentSource) -> DocumentParser:

        if source == DocumentSource.PDF:
            return self._pdf

        if source == DocumentSource.KSEF:
            return self._ksef

        if source == DocumentSource.IMAGE:
            return self._image

        raise ValueError(f"No parser registered for source: {source}")

