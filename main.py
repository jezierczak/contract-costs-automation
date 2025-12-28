import logging

from dotenv import load_dotenv

from contract_costs.services.invoices.parsers.ocr_pdf_invoice_parser import OCRAIAgentInvoiceParser

import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

def main() -> None:

    ai_parser = OCRAIAgentInvoiceParser()

    path = os.path.join(os.getcwd(), "Examples/img20251126_21435673.pdf")

    result = ai_parser.parse(path)

    print(result.invoice)
    print(result.lines)
    print(result.buyer)
    print(result.seller)





if __name__ == '__main__':
    main()

