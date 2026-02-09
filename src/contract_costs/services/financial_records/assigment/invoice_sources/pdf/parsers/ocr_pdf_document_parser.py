import logging
import pytesseract

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import \
    DocumentParseResult

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


logging.basicConfig(level=logging.INFO)


from pathlib import Path

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.document_parser import DocumentParser
from contract_costs.infrastructure.pdf_text_extractor import PdfImageTextExtractor
from contract_costs.infrastructure.openai_invoice_client import OpenAIInvoiceClient
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.ai_invoice_mapper import AIDocumentMapper
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.schema import AI_SCHEMA, AI_PROMPT

logger = logging.getLogger(__name__)

class OCRAIAgentDocumentParser(DocumentParser):

    def __init__(self):
        self._text_extractor = PdfImageTextExtractor()
        self._ai_client = OpenAIInvoiceClient(AI_SCHEMA, AI_PROMPT)
        self._mapper = AIDocumentMapper()

    def parse(self, file_path: Path) -> DocumentParseResult:
        logger.info("Extracting %s with OCR", file_path)

        text = self._text_extractor.extract(file_path)
        logger.debug("OCR text length=%s", len(text))

        logger.info("Parsing %s with AI", file_path)
        ai_data = self._ai_client.extract(text)
        logger.debug(
            "AI raw response keys=%s",
            list(ai_data.keys()) if isinstance(ai_data, dict) else type(ai_data),
        )
        # return ai_data
        return  self._mapper.map(ai_data)

        # return DocumentParseResult(
        #     # raw=ai_data,
        #     record=mapped.record,
        #     lines=mapped.lines,
        #     buyer=mapped.buyer,
        #     seller=mapped.seller,
        # )
