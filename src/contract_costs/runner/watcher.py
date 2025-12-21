import logging
import signal
import sys

from contract_costs.cli.context import Services
from contract_costs.config import INVOICE_INPUT_DIR


def run_watcher(services: Services) -> None:
    logging.info("Starting invoice watcher")
    logging.info("Watching directory: %s", INVOICE_INPUT_DIR)


    watcher = services.invoice_watcher_service

    def shutdown(signum, frame):
        logging.info("Stopping watcher...")
        watcher.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    watcher.run()
