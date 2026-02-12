import time
import logging
import threading
import sys
from uuid import UUID
from pathlib import Path

import contract_costs.config as cfg
from contract_costs.services.documents.upload.dto.upload_document_command import UploadDocumentCommand
from contract_costs.services.queue.document_queue import document_queue
from contract_costs.services.scanner.unprocessed_scanner import scan_unprocessed
from contract_costs.services.watcher.document_watcher import DocumentWatcherService


def run_watcher(*, services, organization_id: UUID, actor_user_id: UUID) -> None:
    document_incoming_dir: Path = (
        cfg.WORK_DIR
        / str(organization_id)
        / cfg.DOCUMENTS_DIR
    )

    logging.info("Starting invoice processing pipeline")
    logging.info("Organization: %s", organization_id)
    logging.info("Watching directory: %s", document_incoming_dir)
    logging.info("Press Ctrl+C to stop")

    watcher = DocumentWatcherService(
        services=services,
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        watch_dir=document_incoming_dir,
    )

    worker = services.document_parse_worker

    # 🔁 scan przy starcie
    action_bus = services.action_bus

    for file in scan_unprocessed(document_incoming_dir):
        action_bus.execute(
            action = UploadDocumentCommand(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                file_path=file,
            ),
            handler=services.upload_document_service
        )

    worker_thread = threading.Thread(
        target=worker.run,
        name=f"invoice-ai-worker-{organization_id}",
        # daemon=True,
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
