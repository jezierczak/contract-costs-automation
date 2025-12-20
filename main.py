import os

from PIL.ImagePath import Path
from dotenv import load_dotenv

from contract_costs.services.invoices.parsers.ocr_pdf_invoice_parser import OCRAIAgentInvoiceParser


def main() -> None:
    load_dotenv()
    ai_parser = OCRAIAgentInvoiceParser()

    path = os.path.join(os.getcwd(), "Examples/Faktura_example.pdf")

    result = ai_parser.parse(path)

    print(result.invoice)
    print(result.lines)
    print(result.buyer)
    print(result.seller)





if __name__ == '__main__':
    main()

