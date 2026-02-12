from pathlib import Path

# ładowanie .env z root projektu
from dotenv import load_dotenv
import os

# -------------------------------------------------
# ENV RESOLUTION (SAFE BY DEFAULT)
# -------------------------------------------------

APP_ENV = os.getenv("APP_ENV", "test")

if APP_ENV not in {"test", "prod"}:
    raise RuntimeError(f"Invalid APP_ENV: {APP_ENV}")

# zawsze najpierw test
load_dotenv(".env.test", override=False)

#  jeśli PROD – jawnie nadpisz
if APP_ENV == "prod":
    load_dotenv(".env.prod", override=True)

def is_test_env() -> bool:
    return APP_ENV == "test"

# --- Excel filenames ---

COMPANY_EXCEL_NAME = "company"

CONTRACT_EXCEL_NAME = "contract"
CONTRACT_PROGRESS_EXCEL_NAME = "contract_progress"

INVOICES_INPUT_NAME = "invoices_input"

DOCUMENTS_INPUT_NAME = "documents_input"

# =========================
# Excel sheet names
# =========================

# Contracts
CONTRACT_METADATA_SHEET_NAME = "contract_metadata"
CONTRACT_ITEMS_SHEET_NAME = "contract_items"

# Companies
COMPANY_METADATA_SHEET_NAME = "company_metadata"
COMPANY_ITEMS_SHEET_NAME = "company_items"  # jeśli będzie

# Invoices
FINANCIAL_RECORD_METADATA_SHEET_NAME = "record_metadata"
FINANCIAL_RECORD_ITEMS_SHEET_NAME = "record_items"

DICTS_BUYERS = "DICTS_BUYERS"
DICTS_SELLERS = "DICTS_SELLERS"
DICTS_AMOUNT_INPUT_TYPES = "DICTS_AMOUNT_INPUT_TYPES"
DICTS_TAX_TREATMENTS = "DICTS_TAX_TREATMENTS"
DICTS_PAYMENT_METHODS ="DICTS_PAYMENT_METHODS"
DICTS_PAYMENT_STATUS ="DICTS_PAYMENT_STATUS"
DICTS_UNITS ="DICTS_UNITS"
DICTS_VAT_RATES = "DICTS_VAT_RATES"
DICTS_ACTIONS = "DICTS_ACTIONS"

DICTS_CONTRACTS ="DICTS_CONTRACTS"
DICTS_COST_NODES ="DICTS_COST_NODES"
DICTS_COST_TYPES ="DICTS_COST_TYPES"

# =========================
# Reoports_prefixes
# =========================


REPORT_CONTRACT_COSTS_PREFIX = "contract_costs"
REPORT_FINANCIAL_RECORD_SUMMARY_PREFIX = "record_summary"

WORK_DIR = Path(os.getenv("WORK_DIR", "./.test_work_dir" if APP_ENV == "test" else "./work_dir"))

# --- owners (archiwum faktur źródłowych) ---
#OWNERS_DIR = WORK_DIR / "companies"
OWNERS_DIR = Path("owners")

# --- invoices (automatyczne) ---
#INCOMING_DIR = WORK_DIR / "incoming"
INCOMING_DIR = Path("incoming")
# -------------------------------------------------
# DOCUMENTS FLOW
# -------------------------------------------------

DOCUMENTS_DIR = INCOMING_DIR / "documents"

DOCUMENTS_PROCESSING_DIR = DOCUMENTS_DIR / "processing"
DOCUMENTS_RAW_DIR = DOCUMENTS_DIR / "raw"
DOCUMENTS_FAILED_DIR = DOCUMENTS_DIR / "failed"
DOCUMENTS_TRASH_DIR = DOCUMENTS_DIR / "trash"
DOCUMENTS_SKIPPED_DIR = DOCUMENTS_DIR / "skipped"
DOCUMENTS_DUPLICATES_DIR = DOCUMENTS_DIR / "duplicates"

# -------------------------------------------------
# RECORD FILE FLOW (relative to org root)
# -------------------------------------------------

RECORD_DRAFT_DIR = Path("draft")
RECORD_RAW_DIR = Path("raw")
RECORD_TRASH_DIR = Path("trash")
RECORD_FAILED_DIR = Path("failed")


# INVOICE_INPUT_DIR = INCOMING_DIR / "invoices"
# INVOICE_FAILED_DIR = INCOMING_DIR / "failed"
# INVOICE_DRAFT_DIR = INCOMING_DIR / "drafts"
# INVOICE_RAW_DIR = INCOMING_DIR / "raw"
# INVOICE_TRASH_DIR = INCOMING_DIR / "trash"

# --- inputs (Excel jako UI) ---
#INPUTS_DIR = WORK_DIR / "inputs"
INPUTS_DIR = Path("inputs")

INPUTS_COMPANIES_DIR = INPUTS_DIR / "companies"
INPUTS_COMPANIES_PROCESSED_DIR = INPUTS_COMPANIES_DIR / "processed"

INPUTS_CONTRACTS_DIR = INPUTS_DIR / "contracts"
INPUTS_CONTRACTS_PROCESSED_DIR = INPUTS_CONTRACTS_DIR / "processed"

INPUTS_INVOICES_DIR = INPUTS_DIR / "invoices"
INPUTS_INVOICES_NEW_DIR = INPUTS_INVOICES_DIR / "new"
INPUTS_INVOICES_ASSIGN_DIR = INPUTS_INVOICES_DIR / "assign"
INPUTS_INVOICES_PROCESSED_DIR = INPUTS_INVOICES_DIR / "processed"

INPUTS_INVOICES_REVIEW_DIR = INPUTS_INVOICES_DIR / "review"
INPUTS_INVOICES_UNPAID_DIR = INPUTS_INVOICES_DIR / "unpaid"
INPUTS_INVOICES_ACCOUNTANT_DIR = INPUTS_INVOICES_DIR / "accountant"

INPUTS_DOCUMENTS_DIR = INPUTS_DIR / "documents"
INPUTS_DOCUMENTS_ASSIGN_DIR = INPUTS_DOCUMENTS_DIR / "assign"


# --- output ---
#REPORTS_DIR = WORK_DIR / "reports"
REPORTS_DIR = Path("reports")

LOGS_DIR = WORK_DIR / "logs"
#SHOW_DIR = WORK_DIR / "show"
SHOW_DIR = Path("show")
CONTRACTS_SHOW_DIR = SHOW_DIR / "contracts"
INVOICES_SHOW_DIR = SHOW_DIR / "invoices"
SNAPSHOTS_SHOW_DIR = SHOW_DIR / "snapshots"
DOCUMENTS_SHOW_DIR =SHOW_DIR / "documents"

# -------------------------------------------------
# DATABASE
# -------------------------------------------------

DB_BACKEND = os.getenv("DB_BACKEND", "memory")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# -------------------------------------------------
# SAFETY CHECK
# -------------------------------------------------

if APP_ENV == "prod" and DB_CONFIG["database"] is None:
    raise RuntimeError("PROD requires explicit DB_NAME")

TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"