from pathlib import Path
import logging
from contract_costs.config import (
    DOCUMENTS_PROCESSING_DIR,
    DOCUMENTS_RAW_DIR,
    DOCUMENTS_FAILED_DIR,
    DOCUMENTS_TRASH_DIR,
    DOCUMENTS_SKIPPED_DIR,
    DOCUMENTS_DUPLICATES_DIR,
)

logger = logging.getLogger(__name__)


class DocumentFileOrganizer:

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

        logger.log(log_level, "Moving document", extra=log_extra)

        file_path.replace(target_path)

        return target_path.relative_to(root)


    @staticmethod
    def move_to_processing(*, root: Path, file_path: Path) -> Path:
        return DocumentFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=DOCUMENTS_PROCESSING_DIR,
        )

    @staticmethod
    def move_to_raw(*, root: Path, file_path: Path) -> Path:
        return DocumentFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=DOCUMENTS_RAW_DIR,
        )

    @staticmethod
    def move_to_failed(*, root: Path, file_path: Path, reason: str) -> Path:
        return DocumentFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=DOCUMENTS_FAILED_DIR / reason.lower(),
            log_level=logging.WARNING,
            extra={"reason": reason},
        )

    @staticmethod
    def move_to_trash(*, root: Path, file_path: Path) -> Path:
        return DocumentFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=DOCUMENTS_TRASH_DIR,
            log_level=logging.WARNING,
        )

    @staticmethod
    def move_to_skipped(*, root: Path, file_path: Path) -> Path:
        return DocumentFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=DOCUMENTS_SKIPPED_DIR,
            log_level=logging.WARNING,
        )

    @staticmethod
    def move_to_duplicates(*, root: Path, file_path: Path) -> Path:
        return DocumentFileOrganizer._move(
            root=root,
            file_path=file_path,
            target_dir=DOCUMENTS_DUPLICATES_DIR,
            log_level=logging.WARNING,
        )

    @staticmethod
    def delete_file(*, root: Path, relative_path: str) -> None:
        """
        Safely deletes a file stored under organization root.

        - Works only on relative paths
        - Prevents path traversal attacks
        - Is idempotent (does nothing if file does not exist)
        """

        if not relative_path:
            logger.warning("delete_file called with empty relative_path")
            return

        root = root.resolve()
        target_path = (root / relative_path).resolve()

        # 🔒 security: ensure file is inside organization root
        if not str(target_path).startswith(str(root)):
            raise RuntimeError(
                f"Refusing to delete file outside organization root: {target_path}"
            )

        if not target_path.exists():
            logger.debug("File already deleted: %s", target_path)
            return

        if target_path.is_dir():
            raise RuntimeError(
                f"Refusing to delete directory: {target_path}"
            )

        try:
            target_path.unlink()
            logger.info("Deleted document file: %s", target_path)
        except Exception:
            logger.exception("Failed to delete file: %s", target_path)
            raise