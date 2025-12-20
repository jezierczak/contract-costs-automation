import logging
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


logging.basicConfig(level=logging.INFO)


from pathlib import Path

from contract_costs.services.invoices.parsers.invoice_parser import InvoiceParser
from contract_costs.services.invoices.dto.parse import InvoiceParseResult
from infrastructure.pdf_text_extractor import PdfTextExtractor
from infrastructure.openai_invoice_client import OpenAIInvoiceClient
from contract_costs.services.invoices.parsers.ai_invoice_mapper import AIInvoiceMapper
from contract_costs.services.invoices.parsers.schema import AI_SCHEMA, AI_PROMPT


class OCRAIAgentInvoiceParser(InvoiceParser):

    def __init__(self):
        self._text_extractor = PdfTextExtractor()
        self._ai_client = OpenAIInvoiceClient(AI_SCHEMA, AI_PROMPT)
        self._mapper = AIInvoiceMapper()

    def parse(self, file_path: Path) -> InvoiceParseResult:
        text = self._text_extractor.extract(file_path)
        print("****************TEXT************************\n")
        print(text)
        ai_data = self._ai_client.extract(text)
        print("****************AI_DATA************************\n")
        print(ai_data)
        return self._mapper.map(ai_data)
