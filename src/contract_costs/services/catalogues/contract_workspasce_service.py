# from pathlib import Path
# import contract_costs.config as cfg
#
#
# class ContractWorkspaceService:
#     def __init__(self, contract_code: str) -> None:
#         self.contract_code = contract_code
#         self.root = cfg.CONTRACTS_DIR / contract_code
#
#     def ensure(self) -> None:
#         for path in [
#             self.watched_invoices_dir,
#             self.excel_dir,
#             self.failed_parse_dir,
#             self.reports_dir,
#         ]:
#             path.mkdir(parents=True, exist_ok=True)
#
#     @property
#     def watched_invoices_dir(self) -> Path:
#         return self.root / "watched" / "invoices"
#
#     @property
#     def excel_dir(self) -> Path:
#         return self.root / "input" / "excel"
#
#     @property
#     def failed_parse_dir(self) -> Path:
#         return self.root / "failed" / "parse"
#
#     @property
#     def reports_dir(self) -> Path:
#         return self.root / "reports"
