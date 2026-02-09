from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DocumentFileOrganizer:

    @staticmethod
    def move_to_processing(*, root: Path, file_path: Path) -> Path:
        target_dir = root / "incoming" / "processing"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.info("Moving document to processing",
                    extra={"source": str(file_path), "target": str(target_path)})

        file_path.replace(target_path)

        return target_path.relative_to(root)


    @staticmethod
    def move_to_raw(*, root: Path, file_path: Path) -> Path:
        target_dir = root / "incoming" / "raw"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.info("Moving document to raw",
                    extra={"source": str(file_path), "target": str(target_path)})

        file_path.replace(target_path)

        return target_path.relative_to(root)


    @staticmethod
    def move_to_failed(*, root: Path, file_path: Path, reason: str) -> Path:
        target_dir = root / "incoming" / "failed" / reason.lower()
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.warning("Moving document to failed",
                       extra={"source": str(file_path),
                              "target": str(target_path),
                              "reason": reason})

        file_path.replace(target_path)

        return target_path.relative_to(root)


    @staticmethod
    def move_to_trash(*, root: Path, file_path: Path) -> Path:
        target_dir = root / "incoming" / "trash"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.info("Moving document to trash",
                    extra={"source": str(file_path), "target": str(target_path)})

        file_path.replace(target_path)

        return target_path.relative_to(root)


    @staticmethod
    def move_to_skipped(*, root: Path, file_path: Path) -> Path:
        target_dir = root / "incoming" / "skipped"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.info("Moving document to skipped",
                    extra={"source": str(file_path), "target": str(target_path)})

        file_path.replace(target_path)

        return target_path.relative_to(root)


    @staticmethod
    def move_to_duplicates(*, root: Path, file_path: Path) -> Path:
        target_dir = root / "incoming" / "duplicates"
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        logger.info("Moving document to duplicates",
                    extra={"source": str(file_path), "target": str(target_path)})

        file_path.replace(target_path)

        return target_path.relative_to(root)