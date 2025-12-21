import time
from pathlib import Path

from contract_costs.infrastructure.filesystem.file_watcher import FileWatcher
from contract_costs.services.invoices.parse_invoice_from_file import (
    ParseInvoiceFromFileService,
)


class InvoiceWatcherService:
    def __init__(
        self,
        watch_dir: Path,
        parse_invoice_service: ParseInvoiceFromFileService,
    ) -> None:
        self._watch_dir = watch_dir
        self._parse_invoice_service = parse_invoice_service
        self.watcher: FileWatcher | None = None

    def run(self) -> None:
        self.watcher = FileWatcher(
            path=self._watch_dir,
            on_file_created=self._handle_file,
        )
        self.watcher.start()


    def stop(self) -> None:
        self.watcher.stop()

    def _handle_file(self, file_path: Path) -> None:
        if not self._wait_until_file_ready(file_path):
            print(f"File not ready: {file_path}")
            return

        try:
            self._parse_invoice_service.execute(file_path)
        except Exception as e:
            # tu później logging
            print(f"Error processing {file_path}: {e}")

    @staticmethod
    def _wait_until_file_ready(file_path, retries=10, delay=0.5):
        for _ in range(retries):
            try:
                with open(file_path, "rb"):
                    return True
            except PermissionError:
                time.sleep(delay)
        return False