
import contract_costs.config as cfg


class WorkDirInitializer:

    @staticmethod
    def execute() -> None:
        dirs = [
            cfg.OWNERS_DIR,
            cfg.CONTRACTS_DIR,
            cfg.REPORTS_DIR,
            cfg.EXPORTS_DIR,
            cfg.INVOICE_INPUT_DIR,
            cfg.INVOICE_FAILED_DIR,
            cfg.LOGS_DIR
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
