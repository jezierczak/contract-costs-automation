import contract_costs.config as cfg

class WorkDirInitializer:
    @staticmethod
    def execute() -> None:
        dirs = [
            cfg.OWNERS_DIR,
            cfg.INVOICE_INPUT_DIR,
            cfg.INVOICE_FAILED_DIR,
            cfg.INPUTS_COMPANIES_NEW_DIR,
            cfg.INPUTS_COMPANIES_EDIT_DIR,
            cfg.INPUTS_COMPANIES_PROCESSED_DIR,
            cfg.INPUTS_CONTRACTS_NEW_DIR,
            cfg.INPUTS_CONTRACTS_EDIT_DIR,
            cfg.INPUTS_CONTRACTS_PROCESSED_DIR,
            cfg.INPUTS_INVOICES_NEW_DIR,
            cfg.INPUTS_INVOICES_ASSIGN_DIR,
            cfg.INPUTS_INVOICES_PROCESSED_DIR,
            cfg.REPORTS_DIR,
            cfg.LOGS_DIR,
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)