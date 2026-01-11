import logging
from pathlib import Path

from dotenv import load_dotenv

from contract_costs.services.invoices.assigment.invoice_sources.pdf.parsers.ocr_pdf_invoice_parser import OCRAIAgentInvoiceParser

import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

def main() -> None:

    # ai_parser = OCRAIAgentInvoiceParser()
    #
    # path = os.path.join(os.getcwd(), "Examples/img20251126_21435673.pdf")
    #
    # result = ai_parser.parse(path)
    #
    # print(result.invoice)
    # print(result.lines)
    # print(result.buyer)
    # print(result.seller)
    #
    # work_dir = Path("base_dir")
    # path = work_dir.resolve()
    # if not (work_dir.exists() or work_dir.is_dir()):
    #     raise RuntimeError(f"Invalid base directory: {work_dir}, {path}")

    # work_dir = Path("work_dir")
    # invoices_path = work_dir / "invoices"
    # # Path.mkdir(invoices_path, exist_ok=True)
    # for item in invoices_path.iterdir():
    # # # for item, dirs, files in os.walk(invoices_path):
    # # #     for filename in files:
    # # for item in invoices_path.glob("**/*.xlsx"):
    #


if __name__ == '__main__':
    main()

