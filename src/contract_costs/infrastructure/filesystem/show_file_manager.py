from datetime import datetime
from pathlib import Path
from uuid import UUID

import contract_costs.config as cfg

class ShowFileManager:
    def __init__(
        self,
        *,
        organization_id: UUID,
        base_dir: Path,
        name: str,
    ) -> None:
        self._org_dir = cfg.WORK_DIR / str(organization_id)
        self._base_dir = self._org_dir / base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._name = name

    def create_output_file(self) -> Path:
        """
        Zwraca NOWĄ ścieżkę outputową z timestampem.
        Niczego nie przenosi.
        """
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._base_dir / f"{self._name}_{ts}.xlsx"

class ContractsShowFileManager(ShowFileManager):
    def __init__(
        self,
        *,
        organization_id: UUID,
        contract_code: str,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            base_dir=cfg.CONTRACTS_SHOW_DIR,
            name=f"contract_{contract_code}",
        )

class SnapshotShowFileManager(ShowFileManager):
    def __init__(
        self,
        *,
        organization_id: UUID,
        contract_code: str,
        contract_date: datetime,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            base_dir=cfg.SNAPSHOTS_SHOW_DIR / contract_code,
            name=f"snapshot_{contract_code}_{contract_date.strftime('%Y%m%d')}",
        )


class SnapshotsShowFileManager(ShowFileManager):
    def __init__(
        self,
        *,
        organization_id: UUID,
        contract_code: str,
    ) -> None:
        super().__init__(
            organization_id=organization_id,
            base_dir=cfg.SNAPSHOTS_SHOW_DIR,
            name=f"snapshots_{contract_code}",
        )




class FinancialRecordShowFileManager(ShowFileManager):
    def __init__(
        self,
        *,
        organization_id: UUID,
        view,
    ):
        super().__init__(
            organization_id=organization_id,
            base_dir=cfg.INVOICES_SHOW_DIR / view.value,
            name=f"records_{view.value}",
        )


class FinancialRecordsShowFileManager(ShowFileManager):
    def __init__(
        self,
        *,
        organization_id: UUID,
        prefix: str,
    ):
        super().__init__(
            organization_id=organization_id,
            base_dir=cfg.INVOICES_SHOW_DIR / prefix,
            name=f"records_{prefix}",
        )

class DocumentsShowFileManager(ShowFileManager):
    def __init__(
        self,
        *,
        organization_id: UUID,
        prefix: str,
    ):
        super().__init__(
            organization_id=organization_id,
            base_dir=cfg.DOCUMENTS_SHOW_DIR / prefix,
            name=f"records_{prefix}",
        )
