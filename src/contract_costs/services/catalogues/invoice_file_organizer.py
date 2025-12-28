import logging
import re
from datetime import date
from pathlib import Path

from contract_costs.model.company import Company
import contract_costs.config as cfg

logger = logging.getLogger(__name__)


class InvoiceFileOrganizer:

    @staticmethod
    def move_to_owner(
        file_path: Path,
        owner: Company,
        issue_date: date,
        seller_name: str,
        invoice_number: str,
    ) -> Path:

        seller_name = seller_name or "UNKNOWN"
        invoice_number = invoice_number or "NO_NUMBER"

        safe_owner = InvoiceFileOrganizer._sanitize_filename(owner.name)

        target_dir = (
            cfg.OWNERS_DIR
            / safe_owner
            / "invoices"
            / str(issue_date.year)
            / f"{issue_date.month:02d}"
        )
        target_dir.mkdir(parents=True, exist_ok=True)

        new_name = InvoiceFileOrganizer._build_invoice_filename(
            seller_name=seller_name,
            invoice_number=invoice_number,
            original=file_path,
        )

        target_path = target_dir / new_name

        logger.info(
            "Moving invoice file to owner directory",
            extra={
                "source": str(file_path),
                "target": str(target_path),
                "owner": owner.tax_number,
            },
        )

        file_path.replace(target_path)
        return target_path

    @staticmethod
    def move_to_failed(
            file_path: Path,
            reason: str,
    ) -> Path:
        target_dir = cfg.INVOICE_FAILED_DIR / reason.lower()
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.warning(
            "Moving invoice file to failed directory",
            extra={
                "source": str(file_path),
                "target": str(target_path),
                "reason": reason,
            },
        )

        file_path.replace(target_path)
        return target_path

    @staticmethod
    def _build_invoice_filename(
        seller_name: str,
        invoice_number: str,
        original: Path,
    ) -> str:
        s_name = InvoiceFileOrganizer._sanitize_filename(seller_name)[:5]
        i_number = InvoiceFileOrganizer._sanitize_filename(invoice_number)
        return f"{s_name}_{i_number}{original.suffix}"

    @staticmethod
    def _sanitize_filename(value: str) -> str:
        value = value.strip().upper()
        value = re.sub(r"[\\/:*?\"<>|]", "_", value)
        value = re.sub(r"\s+", "_", value)
        return value
