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
COMPANY_EXCEL_FILENAME = "company.xlsx"
COMPANY_EDIT_EXCEL_TEMPLATE = "company_{ref}.xlsx"

CONTRACT_EXCEL_FILENAME = "contract.xlsx"
CONTRACT_EDIT_EXCEL_TEMPLATE = "contract_{code}.xlsx"

# INVOICES_EXCEL_FILENAME = "invoices.xlsx"
# INVOICES_ASSIGN_EXCEL_FILENAME = "invoice_assignment.xlsx"

INVOICES_EXCEL_FILENAME = "invoices_input.xlsx"
#INVOICES_EXCEL_FILENAME_IN_PROGRESS = "invoices_in_progress.xlsx"

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
INVOICE_METADATA_SHEET_NAME = "invoice_metadata"
INVOICE_ITEMS_SHEET_NAME = "invoice_items"

DICTS_BUYERS = "DICTS_BUYERS"
DICTS_SELLERS = "DICTS_SELLERS"
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
REPORT_INVOICE_SUMMARY_PREFIX = "invoice_summary"

WORK_DIR = Path(os.getenv("WORK_DIR", "./.test_work_dir" if APP_ENV == "test" else "./work_dir"))

# --- owners (archiwum faktur źródłowych) ---
OWNERS_DIR = WORK_DIR / "companies"

# --- invoices (automatyczne) ---
INVOICES_DIR = WORK_DIR / "invoices"
INVOICE_INPUT_DIR = INVOICES_DIR / "incoming"
INVOICE_FAILED_DIR = INVOICES_DIR / "failed"

# --- inputs (Excel jako UI) ---
INPUTS_DIR = WORK_DIR / "inputs"

INPUTS_COMPANIES_DIR = INPUTS_DIR / "companies"
INPUTS_COMPANIES_NEW_DIR = INPUTS_COMPANIES_DIR / "new"
INPUTS_COMPANIES_EDIT_DIR = INPUTS_COMPANIES_DIR / "edit"
INPUTS_COMPANIES_PROCESSED_DIR = INPUTS_COMPANIES_DIR / "processed"

INPUTS_CONTRACTS_DIR = INPUTS_DIR / "contracts"
INPUTS_CONTRACTS_NEW_DIR = INPUTS_CONTRACTS_DIR / "new"
INPUTS_CONTRACTS_EDIT_DIR = INPUTS_CONTRACTS_DIR / "edit"
INPUTS_CONTRACTS_PROCESSED_DIR = INPUTS_CONTRACTS_DIR / "processed"

INPUTS_INVOICES_DIR = INPUTS_DIR / "invoices"
INPUTS_INVOICES_NEW_DIR = INPUTS_INVOICES_DIR / "new"
INPUTS_INVOICES_ASSIGN_DIR = INPUTS_INVOICES_DIR / "assign"
INPUTS_INVOICES_PROCESSED_DIR = INPUTS_INVOICES_DIR / "processed"

# --- output ---
REPORTS_DIR = WORK_DIR / "reports"
LOGS_DIR = WORK_DIR / "logs"

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