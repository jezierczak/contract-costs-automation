from pathlib import Path

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.document_parser import \
    DocumentParser
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import \
    DocumentParseResult


class KsefDocumentParser(DocumentParser):

    def parse(self, file_path: Path) -> DocumentParseResult:
        raise NotImplementedError("KsefDocumentParser not implemented")