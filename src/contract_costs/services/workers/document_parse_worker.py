import time
import logging
from queue import Empty
from multiprocessing import Process
from uuid import UUID

from contract_costs.model.document import DocumentSource
from contract_costs.services.documents.exeptions import DocumentFatalError
from contract_costs.services.documents.process.dto.process_document_command import (
    ProcessDocumentCommand,
)
from contract_costs.services.queue.document_queue import document_queue

logger = logging.getLogger(__name__)


MAX_RETRIES = 3


def process_document_in_subprocess(
    organization_id: UUID,
    actor_id: UUID,
    document_id: UUID,
):
    print("SUBPROCESS STARTED")
    from contract_costs.cli.context import get_services

    try:
        services = get_services()

        services.action_bus.execute(
            action=ProcessDocumentCommand(
                organization_id=organization_id,
                actor_user_id=actor_id,
                document_id=document_id,
            ),
            handler=services.process_document_service
        )


    except DocumentFatalError:
        logger.exception("Fatal parse error")
        exit(100)  # specjalny exitcode

    except Exception:
        logger.exception("Retryable error")
        raise
        # logger.exception(
        #     "Subprocess failed while processing document %s (org=%s user=%s)",
        #     document_id,
        #     organization_id,
        #     actor_id,
        # )
        # raise


class DocumentParseWorker:
    def __init__(self, rpm: int = 3, timeout: int = 180) -> None:
        self._sleep = 60 / rpm  # poprawione
        self._timeout = timeout
        self._running = True

    def run(self) -> None:
        logger.info("Document parse worker started")

        while self._running:
            try:
                organization_id, actor_id, document_id = document_queue.get(timeout=1)
            except Empty:
                continue

            try:
                self._process_with_retry(
                    organization_id,
                    actor_id,
                    document_id,
                )

            except Exception:
                logger.exception(
                    "Document permanently failed after retries (org=%s user=%s doc=%s)",
                    organization_id,
                    actor_id,
                    document_id,
                )


            finally:
                document_queue.task_done()

                if self._running:
                    from contract_costs.cli.context import get_services
                    services = get_services()
                    document = services.document_repository.get(
                        organization_id=organization_id,
                        document_id=document_id,
                    )
                    if document and document.document_source != DocumentSource.KSEF:
                        time.sleep(self._sleep)

    def _process_with_retry(
        self,
        organization_id: UUID,
        actor_id: UUID,
        document_id: UUID,
    ) -> None:

        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(
                "Processing document (attempt %s/%s) org=%s user=%s doc=%s",
                attempt,
                MAX_RETRIES,
                organization_id,
                actor_id,
                document_id,
            )

            p = Process(
                target=process_document_in_subprocess,
                args=(organization_id, actor_id, document_id),
                # daemon=True,
            )
            p.start()
            p.join(timeout=self._timeout)
            if p.exitcode == 100:
                logger.error("Fatal error — no retry")
                return
            # Timeout
            if p.is_alive():
                logger.error(
                    "Timeout on attempt %s (org=%s user=%s doc=%s)",
                    attempt,
                    organization_id,
                    actor_id,
                    document_id,
                )
                p.terminate()
                p.join()

                if attempt == MAX_RETRIES:
                    raise TimeoutError("Max retries reached due to timeout")

                time.sleep(2 * attempt)  # prosty backoff
                continue

            # Subprocess zakończył się
            if p.exitcode != 0:
                logger.error(
                    "Subprocess crashed (exitcode=%s) on attempt %s (doc=%s)",
                    p.exitcode,
                    attempt,
                    document_id,
                )

                if attempt == MAX_RETRIES:
                    raise RuntimeError("Max retries reached due to subprocess error")

                time.sleep(2 * attempt)
                continue

            # Sukces
            logger.info(
                "Document processed successfully (org=%s user=%s doc=%s)",
                organization_id,
                actor_id,
                document_id,
            )
            return

    def stop(self) -> None:
        logger.info("Stopping document parse worker")
        self._running = False
