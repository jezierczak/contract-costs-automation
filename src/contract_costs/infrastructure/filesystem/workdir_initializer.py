from uuid import UUID

import contract_costs.config as cfg

class WorkDirInitializer:
    @staticmethod
    def execute(*, organization_id: UUID) -> None:
        org_root = cfg.WORK_DIR / str(organization_id)

        dirs = [
            # owners
            org_root / cfg.OWNERS_DIR,

            # incoming (OCR / raw invoices)
            org_root / cfg.DOCUMENTS_DIR,
            org_root / cfg.DOCUMENTS_FAILED_DIR,
            org_root / cfg.DOCUMENTS_PROCESSING_DIR,
            org_root / cfg.DOCUMENTS_TRASH_DIR,
            org_root / cfg.DOCUMENTS_RAW_DIR,
            org_root / cfg.DOCUMENTS_SKIPPED_DIR,
            org_root / cfg.DOCUMENTS_DUPLICATES_DIR,
            # inputs (Excel UI)
            org_root / cfg.INPUTS_COMPANIES_DIR,
            org_root / cfg.INPUTS_CONTRACTS_DIR,
            org_root / cfg.INPUTS_INVOICES_ASSIGN_DIR,
            org_root / cfg.INPUTS_INVOICES_NEW_DIR,
            org_root / cfg.INPUTS_INVOICES_REVIEW_DIR,
            org_root / cfg.INPUTS_INVOICES_UNPAID_DIR,
            org_root / cfg.INPUTS_INVOICES_ACCOUNTANT_DIR,

            # outputs
            org_root / cfg.REPORTS_DIR,
            org_root / cfg.SHOW_DIR / "contracts",
            org_root / cfg.SHOW_DIR / "invoices",
            org_root / cfg.SHOW_DIR / "snapshots",

            # logs (global zostawiasz, więc opcjonalnie)
            cfg.LOGS_DIR,
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)