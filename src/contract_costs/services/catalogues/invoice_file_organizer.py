from pathlib import Path
from datetime import date
import logging

import contract_costs.config as cfg
from contract_costs.model.company import Company

logger = logging.getLogger(__name__)


class InvoiceFileOrganizer:
    """
    Odpowiada WYŁĄCZNIE za fizyczne przenoszenie plików faktur
    po parsowaniu.
    """
    @staticmethod
    def move_to_owner(
        file_path: Path,
        owner: Company,
        issue_date: date,
    ) -> Path:
        """
        Przenosi plik faktury do katalogu ownera,
        pogrupowanego po roku / miesiącu.
        """
        target_dir = (
            cfg.OWNERS_DIR
            / owner.tax_number
            / "invoices"
            / str(issue_date.year)
            / f"{issue_date.month:02d}"
        )

        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

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
        """
        Przenosi plik faktury do katalogu failed.
        """
        target_dir = cfg.WORK_DIR / "failed" / reason.lower()
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
