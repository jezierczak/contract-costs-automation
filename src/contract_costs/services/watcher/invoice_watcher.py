import logging
import time
from pathlib import Path

from contract_costs.infrastructure.filesystem.file_watcher import FileWatcher
from contract_costs.services.queue.invoice_queue import invoice_queue

logger = logging.getLogger(__name__)


class InvoiceWatcherService:
    def __init__(self, watch_dir: Path) -> None:
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

        logger.info("Enqueuing new invoice file: %s", file_path)
        invoice_queue.put(file_path)

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
