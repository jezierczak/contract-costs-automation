import time
import logging
from pathlib import Path
from queue import Empty
from multiprocessing import Process

from contract_costs.services.queue.invoice_queue import invoice_queue
from contract_costs.services.invoices.parse_invoice_from_file import (
    ParseInvoiceFromFileService,
)

logger = logging.getLogger(__name__)

def process_invoice_in_subprocess(file_path: Path):
    """
    URUCHAMIANA W OSOBNYM PROCESIE.
    NIE WOLNO tu nic importować globalnie, co tworzy locki.
    """
    from contract_costs.cli.context import get_services


    logger.info("Subprocess started for %s", file_path)

    services = get_services()
    parser = services.parse_invoice_from_file

    parser.execute(file_path)


class InvoiceAIWorker:
    def __init__(self, rpm: int = 3, timeout: int = 180) -> None:
        self._sleep = 65 / rpm
        self._timeout = timeout
        self._running = True

    def run(self) -> None:
        logger.info("AI worker started")

        while self._running:
            try:
                file_path: Path = invoice_queue.get(timeout=1)
            except Empty:
                continue

            try:
                logger.info("Processing invoice via AI (process): %s", file_path)

                p = Process(
                    target=process_invoice_in_subprocess,
                    args=(file_path,),
                )
                p.start()
                p.join(timeout=self._timeout)

                if p.is_alive():
                    logger.error(
                        "Invoice processing timed out, killing process: %s",
                        file_path,
                    )
                    p.terminate()
                    p.join()

            except Exception:
                logger.exception("AI processing failed: %s", file_path)

            finally:
                invoice_queue.task_done()
                if self._running:
                    time.sleep(self._sleep)

    def stop(self) -> None:
        logger.info("Stopping AI worker")
        self._running = False
