from datetime import datetime
from pathlib import Path

import contract_costs.config as cfg

class ShowFileManager:
    def __init__(self, base_dir: Path, name: str) -> None:
        self._base_dir = base_dir
        self._name = name

    def create_output_file(self) -> Path:
        """
        Zwraca NOWĄ ścieżkę outputową z timestampem.
        Niczego nie przenosi.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._base_dir / f"{self._name}_{ts}.xlsx"

class ContractsShowFileManager(ShowFileManager):
    def __init__(self, contract_code: str) -> None:
        path = cfg.CONTRACTS_SHOW_DIR
        name = f"contract_{contract_code}"
        super().__init__(Path(path), name)

class SnapshotShowFileManager(ShowFileManager):
    def __init__(self, contract_code: str,contract_date: datetime) -> None:
        path = cfg.SNAPSHOTS_SHOW_DIR / f"{contract_code}"
        name = f"snapshot_{contract_code}_{contract_date.strftime("%Y%m%d")}"
        super().__init__(Path(path), name)

class SnapshotsShowFileManager(ShowFileManager):
    def __init__(self,  contract_code: str) -> None:
        path = cfg.SNAPSHOTS_SHOW_DIR
        name = f"snapshots_{contract_code}"
        super().__init__(Path(path), name)



class InvoiceShowFileManager(ShowFileManager):
    def __init__(self, *, view):
        base_dir = cfg.INVOICES_SHOW_DIR / view.value
        base_dir.mkdir(parents=True, exist_ok=True)
        name = f"invoices_{view.value}"
        super().__init__(base_dir,name)

class InvoicesShowFileManager(ShowFileManager):
    def __init__(self, *, prefix: str):
        base_dir = cfg.INVOICES_SHOW_DIR / prefix
        base_dir.mkdir(parents=True, exist_ok=True)
        name = f"invoices_{prefix}"
        super().__init__(base_dir,name)