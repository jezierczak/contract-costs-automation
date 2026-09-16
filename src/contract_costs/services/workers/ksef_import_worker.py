import logging
from dataclasses import replace
from queue import Empty

import contract_costs.config as cfg
from contract_costs.common.time import utc_now
from contract_costs.services.documents.exeptions import DuplicateDocument
from contract_costs.services.documents.upload.dto.upload_document_command import UploadDocumentCommand
from contract_costs.services.queue.ksef_import_queue import ksef_import_queue

logger = logging.getLogger(__name__)


class KsefImportWorker:
    def __init__(self) -> None:
        self._running = True

    def run(self) -> None:
        logger.info("KSeF import worker started")

        while self._running:
            try:
                item = ksef_import_queue.get(timeout=1)
            except Empty:
                continue

            try:
                self._process_item(item)
            except Exception:
                logger.exception(
                    "KSeF import job failed (org=%s company=%s from=%s to=%s)",
                    item.organization_id,
                    item.company_id,
                    item.from_date,
                    item.to_date,
                )
            finally:
                ksef_import_queue.task_done()

    def _process_item(self, item) -> None:
        from contract_costs.cli.context import get_services

        services = get_services()
        now = utc_now()

        with services.uow as uow:
            company = uow.companies.get(
                item.company_id,
                item.organization_id,
            )
            settings = uow.company_ksef_settings.get_by_company_id(
                organization_id=item.organization_id,
                company_id=item.company_id,
            )
            if company is None:
                logger.warning(
                    "Skipping KSeF import. Company not found (org=%s company=%s)",
                    item.organization_id,
                    item.company_id,
                )
                return
            if settings is None or not settings.is_enabled:
                logger.warning(
                    "Skipping KSeF import. Missing or disabled settings (org=%s company=%s)",
                    item.organization_id,
                    item.company_id,
                )
                return

        imported = 0
        duplicates = 0
        try:
            invoices = services.ksef_api_client.fetch_invoice_xmls(
                settings=settings,
                company=company,
                from_date=item.from_date,
                to_date=item.to_date,
            )
            incoming_dir = (
                cfg.WORK_DIR
                / str(item.organization_id)
                / cfg.DOCUMENTS_DIR
                / "incoming"
            )
            incoming_dir.mkdir(parents=True, exist_ok=True)

            for invoice in invoices:
                target = incoming_dir / self._safe_filename(invoice.filename)
                target.write_bytes(invoice.xml_content)
                try:
                    services.action_bus.execute(
                        action=UploadDocumentCommand(
                            organization_id=item.organization_id,
                            actor_user_id=item.actor_user_id,
                            file_path=target,
                        ),
                        handler=services.upload_document_service,
                    )
                    imported += 1
                except DuplicateDocument:
                    duplicates += 1
                    if target.exists():
                        target.unlink(missing_ok=True)

            self._update_settings_success(
                services=services,
                item=item,
                now=now,
            )
            logger.info(
                "KSeF import processed (org=%s company=%s imported=%s duplicates=%s from=%s to=%s)",
                item.organization_id,
                item.company_id,
                imported,
                duplicates,
                item.from_date,
                item.to_date,
            )
        except Exception as exc:
            self._update_settings_error(
                services=services,
                item=item,
                now=now,
                error_message=str(exc),
            )
            raise

    @staticmethod
    def _safe_filename(filename: str) -> str:
        invalid = '<>:"/\\|?*'
        sanitized = "".join("_" if ch in invalid else ch for ch in filename)
        return sanitized or "ksef_invoice.xml"

    def _update_settings_success(self, *, services, item, now) -> None:
        with services.uow as uow:
            settings = uow.company_ksef_settings.get_by_company_id(
                organization_id=item.organization_id,
                company_id=item.company_id,
            )
            if settings is None:
                return
            updated = replace(
                settings,
                last_import_from=item.to_date,
                last_import_at=now,
                last_error=None,
                updated_at=now,
                updated_by_user_id=item.actor_user_id,
            )
            uow.company_ksef_settings.update(
                organization_id=item.organization_id,
                settings=updated,
            )

    def _update_settings_error(self, *, services, item, now, error_message: str) -> None:
        with services.uow as uow:
            settings = uow.company_ksef_settings.get_by_company_id(
                organization_id=item.organization_id,
                company_id=item.company_id,
            )
            if settings is None:
                return
            updated = replace(
                settings,
                last_import_at=now,
                last_error=error_message[:1000],
                updated_at=now,
                updated_by_user_id=item.actor_user_id,
            )
            uow.company_ksef_settings.update(
                organization_id=item.organization_id,
                settings=updated,
            )

    def stop(self) -> None:
        logger.info("Stopping KSeF import worker")
        self._running = False
