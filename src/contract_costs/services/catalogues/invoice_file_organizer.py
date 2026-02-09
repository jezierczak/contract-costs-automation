import logging
import re
from datetime import date
from pathlib import Path
from typing import Literal

from contract_costs.model.company import Company

logger = logging.getLogger(__name__)


class RecordFileOrganizer:

    # =====================================================
    # OWNER (cost / revenue)
    # =====================================================

    @staticmethod
    def move_to_owner(
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

        safe_owner = RecordFileOrganizer._sanitize_filename(owner.name)
        doc_type = "costs" if kind == "cost" else "revenues"

        target_dir = (
            root
            / "owners"
            / safe_owner
            / doc_type
            / "invoices"
            / str(issue_date.year)
            / f"{issue_date.month:02d}"
        )
        target_dir.mkdir(parents=True, exist_ok=True)

        new_name = RecordFileOrganizer._build_invoice_filename(
            client_name=client_name,
            invoice_number=record_ref_number,
            original=file_path,
        )

        target_path = target_dir / new_name

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

    # =====================================================
    # DRAFT
    # =====================================================

    @staticmethod
    def move_to_draft(
        *,
        root: Path,
        file_path: Path,
    ) -> Path:

        target_dir = root / "draft"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.info(
            "Moving record file to draft directory",
            extra={
                "source": str(file_path),
                "target": str(target_path),
            },
        )

        file_path.replace(target_path)
        return target_path.relative_to(root)

    # =====================================================
    # RAW
    # =====================================================

    @staticmethod
    def move_to_raw(
        *,
        root: Path,
        file_path: Path,
    ) -> Path:

        target_dir = root / "raw"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.info(
            "Moving record file to raw directory",
            extra={
                "source": str(file_path),
                "target": str(target_path),
            },
        )

        file_path.replace(target_path)
        return target_path.relative_to(root)

    # =====================================================
    # TRASH
    # =====================================================

    @staticmethod
    def move_to_trash(
        *,
        root: Path,
        file_path: Path,
    ) -> Path:

        target_dir = root / "trash"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.info(
            "Moving record file to trash directory",
            extra={
                "source": str(file_path),
                "target": str(target_path),
            },
        )

        file_path.replace(target_path)
        return target_path.relative_to(root)

    # =====================================================
    # FAILED
    # =====================================================

    @staticmethod
    def move_to_failed(
        *,
        root: Path,
        file_path: Path,
        reason: str,
    ) -> Path:

        target_dir = root / "failed" / reason.lower()
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.warning(
            "Moving record file to failed directory",
            extra={
                "source": str(file_path),
                "target": str(target_path),
                "reason": reason,
            },
        )

        file_path.replace(target_path)
        return target_path.relative_to(root)

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
        return f"{s_name}_{i_number}{original.suffix}"

    @staticmethod
    def _sanitize_filename(value: str) -> str:
        value = value.strip().upper()
        value = re.sub(r"[\\/:*?\"<>|]", "_", value)
        value = re.sub(r"\s+", "_", value)
        return value
