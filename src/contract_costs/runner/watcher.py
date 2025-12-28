import time
import logging
import threading
import sys

from contract_costs.config import INVOICE_INPUT_DIR
from contract_costs.services.queue.invoice_queue import invoice_queue
from contract_costs.services.scanner.unprocessed_scanner import scan_unprocessed


def run_watcher(services) -> None:
    logging.info("Starting invoice processing pipeline")
    logging.info("Watching directory: %s", INVOICE_INPUT_DIR)
    logging.info("Press Ctrl+C to stop")

    watcher = services.invoice_watcher_service
    worker = services.invoice_ai_worker

    # scan przy starcie
    for file in scan_unprocessed(INVOICE_INPUT_DIR):
        invoice_queue.put(file)

    worker_thread = threading.Thread(
        target=worker.run,
        name="invoice-ai-worker",
    )
    worker_thread.start()

    watcher.run()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Ctrl+C received, shutting down...")
        watcher.stop()
        worker.stop()
        worker_thread.join(timeout=5)
        logging.info("Shutdown complete")
        sys.exit(0)
