import logging
from pathlib import Path

from contract_costs.model.document import DocumentSource
from contract_costs.services.documents.process.document_parser_resolver import DocumentParserResolver
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import DocumentParseResult


logger=logging.getLogger(__name__)


class ParseDocumentFromFileService:

    def __init__(
        self,
        parser_resolver: DocumentParserResolver,
    ):
        self._resolver = parser_resolver

    def execute(
        self,
        *,
        file_path: Path,
        source: DocumentSource,
    ) -> DocumentParseResult:

        parser = self._resolver.resolve(source)

        return parser.parse(file_path)

