import logging
import pytesseract



pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


logging.basicConfig(level=logging.INFO)


from pathlib import Path

from contract_costs.services.invoices.parsers.invoice_parser import InvoiceParser
from contract_costs.services.invoices.dto.parse import InvoiceParseResult
from contract_costs.infrastructure.pdf_text_extractor import PdfTextExtractor
from contract_costs.infrastructure.openai_invoice_client import OpenAIInvoiceClient
from contract_costs.services.invoices.parsers.ai_invoice_mapper import AIInvoiceMapper
from contract_costs.services.invoices.parsers.schema import AI_SCHEMA, AI_PROMPT

logger = logging.getLogger(__name__)

class OCRAIAgentInvoiceParser(InvoiceParser):

    def __init__(self):
        self._text_extractor = PdfTextExtractor()
        self._ai_client = OpenAIInvoiceClient(AI_SCHEMA, AI_PROMPT)
        self._mapper = AIInvoiceMapper()

    def parse(self, file_path: Path) -> InvoiceParseResult:
        logger.info(f"Extracting {file_path} with PDF parser")

        text = self._text_extractor.extract(file_path)
        print("****************TEXT************************\n")
        print(text)

        logger.info("Parsing %s with AI", file_path)

        try:
            ai_data = self._ai_client.extract(text)
        except Exception:
            logger.exception("AI extraction failed for %s", file_path)
            raise
        print("****************AI_DATA************************\n")
        print(ai_data)

        try:
            return self._mapper.map(ai_data)
        except Exception:
            logger.exception("AI mapping failed for %s", file_path)
            raise
