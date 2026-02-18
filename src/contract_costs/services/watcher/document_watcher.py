import logging
import time
from pathlib import Path
from uuid import UUID

from contract_costs.infrastructure.filesystem.file_watcher import FileWatcher
from contract_costs.services.documents.upload.dto.upload_document_command import UploadDocumentCommand

logger = logging.getLogger(__name__)


class DocumentWatcherService:
    def __init__(
        self,
        *,
        services,
        organization_id: UUID,
        actor_user_id: UUID,
        watch_dir: Path,
    ) -> None:
        self._services = services
        self._organization_id = organization_id
        self._actor_user_id = actor_user_id
        self._watch_dir = watch_dir
        self.watcher: FileWatcher | None = None


    def run(self) -> None:
        self.watcher = FileWatcher(
            path=self._watch_dir,
            on_file_created=self._handle_file,
        )
        self.watcher.start()

    def stop(self) -> None:
        if self.watcher:
            self.watcher.stop()

    def _handle_file(self, file_path: Path) -> None:
        if not self._wait_until_file_ready(file_path):
            logger.warning("File not ready: %s", file_path)
            return

        logger.info(
            "Enqueuing new invoice file: %s (org=%s)",
            file_path,
            self._organization_id,
        )

        self._services.action_bus.execute(
            action=UploadDocumentCommand(
                organization_id=self._organization_id,
                actor_user_id=self._actor_user_id,
                file_path=file_path,
            ),
            handler=self._services.upload_document_service,
        )

    @staticmethod
    def _wait_until_file_ready(
        file_path: Path,
        retries: int = 10,
        delay: float = 0.5,
    ) -> bool:
        for _ in range(retries):
            try:
                with open(file_path, "rb"):
                    return True
            except PermissionError:
                time.sleep(delay)
        return False

