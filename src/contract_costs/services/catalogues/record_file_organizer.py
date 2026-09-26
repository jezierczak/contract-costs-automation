import logging
import re
import uuid
from datetime import date
from pathlib import Path
from typing import Literal

from contract_costs.model.company import Company
import contract_costs.config as cfg

logger = logging.getLogger(__name__)


class RecordFileOrganizer:

    # =====================================================
    # INTERNAL MOVE
    # =====================================================

    @staticmethod
    def _move(
        *,
        root: Path,
        file_path: Path,
        target_dir: Path,
        log_level: int = logging.INFO,
        extra: dict | None = None,
    ) -> Path:

        full_dir = root / target_dir
        full_dir.mkdir(parents=True, exist_ok=True)

        target_path = full_dir / file_path.name

        log_extra = {
            "source": str(file_path),
            "target": str(target_path),
        }

        if extra:
            log_extra.update(extra)

        logger.log(log_level, "Moving record file", extra=log_extra)

        file_path.replace(target_path)

        return target_path.relative_to(root)

    def move_to_owner(
        self,
        *,
        root: Path,
        file_path: Path,
        owner: Company,
        kind: Literal["cost", "revenue"],
        issue_date: date | None,
        client_name: str,
        record_ref_number: str,
    ) -> Path:

        client_name = client_name or "UNKNOWN"
        record_ref_number = record_ref_number or "NO_NUMBER"
        issue_date = issue_date or date.today()

        safe_owner = self._sanitize_filename(owner.name)
        doc_type = "costs" if kind == "cost" else "revenues"

        target_dir = (
            cfg.OWNERS_DIR
            / safe_owner
            / doc_type
            / "invoices"
            / str(issue_date.year)
            / f"{issue_date.month:02d}"
        )

        new_name = RecordFileOrganizer._build_invoice_filename(
            client_name=client_name,
            invoice_number=record_ref_number,
            original=file_path,
        )

        full_dir = root / target_dir
        full_dir.mkdir(parents=True, exist_ok=True)

        target_path = full_dir / new_name

        logger.info(
            "Moving record file to owner directory",
            extra={
                "source": str(file_path),
                "target": str(target_path),
                "owner": owner.tax_number,
            },
        )

        file_path.replace(target_path)

        return target_path.relative_to(root)

    @staticmethod
    def move_to_draft(*, root: Path, file_path: Path) -> Path:
        return RecordFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=cfg.RECORD_DRAFT_DIR,
        )

    @staticmethod
    def move_to_raw(*, root: Path, file_path: Path) -> Path:
        return RecordFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=cfg.RECORD_RAW_DIR,
        )

    @staticmethod
    def move_to_trash(*, root: Path, file_path: Path) -> Path:
        return RecordFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=cfg.RECORD_TRASH_DIR,
        )

    @staticmethod
    def move_to_failed(*, root: Path, file_path: Path, reason: str) -> Path:
        safe_reason = RecordFileOrganizer._sanitize_filename(reason)

        return RecordFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=cfg.RECORD_FAILED_DIR / safe_reason.lower(),
            log_level=logging.WARNING,
            extra={"reason": reason},
        )

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _build_invoice_filename(
        *,
        client_name: str,
        invoice_number: str,
        original: Path,
    ) -> str:
        s_name = RecordFileOrganizer._sanitize_filename(client_name)[:5]
        i_number = RecordFileOrganizer._sanitize_filename(invoice_number)
        uid = uuid.uuid4().hex[:6]  # 🔥 krótki losowy

        return f"{s_name}_{i_number}_{uid}{original.suffix}"

    @staticmethod
    def _sanitize_filename(value: str) -> str:
        if not value:
            return "UNKNOWN"

        value = value.strip().upper()

        # usuń niedozwolone znaki systemowe
        value = re.sub(r"[\\/:*?\"<>|]", "_", value)

        # zamień whitespace na _
        value = re.sub(r"\s+", "_", value)

        # usuń podwójne _
        value = re.sub(r"_+", "_", value)

        # Windows po cichu obcina kropki/spacje na końcu nazwy – bez tego np.
        # „SP. Z O.O.” daje katalog, który w kontenerze (Linux) i na hoście
        # (Windows) jest dwoma różnymi katalogami
        value = value.rstrip(". ")

        return value or "UNKNOWN"
