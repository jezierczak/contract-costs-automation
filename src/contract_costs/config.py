from pathlib import Path
import os
from dotenv import load_dotenv

# ładowanie .env z root projektu
load_dotenv()

CONTRACT_EDIT_FILE_NAME = "contract_edit.xlsx"
CONTRACT_METADATA_SHEET_NAME = "contract_metadata"
CONTRACT_ITEMS_SHEET_NAME = "contract_items"

load_dotenv()

WORK_DIR = Path(os.getenv("WORK_DIR", "./work_dir"))

INVOICE_INPUT_DIR = WORK_DIR / os.getenv(
    "INVOICE_INPUT_DIR", "invoices/incoming"
)

INVOICE_FAILED_DIR = WORK_DIR / os.getenv(
    "INVOICE_FAILED_DIR", "invoices/failed"
)

CONTRACTS_DIR = WORK_DIR / os.getenv(
    "CONTRACTS_DIR", "contracts"
)

EXPORTS_DIR = WORK_DIR / os.getenv(
    "EXPORTS_DIR", "exports"
)

REPORTS_DIR = WORK_DIR / os.getenv(
    "REPORTS_DIR", "reports"
)

OWNERS_DIR = WORK_DIR / os.getenv(
    "OWNERS_DIR", "companies"
)

LOGS_DIR = WORK_DIR / os.getenv(
    "LOGS_DIR", "logs"
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}