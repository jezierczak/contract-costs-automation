import json
import logging
from dataclasses import asdict, replace
from datetime import date
from decimal import Decimal
from enum import Enum

import contract_costs.config as cfg
from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.business_event import BusinessEventLevel
from contract_costs.model.document import DocumentStatus, DocumentSource
from contract_costs.services.business_event.business_event_service import BusinessEventService
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.documents.apply.apply_document_service import ApplyDocumentService
from contract_costs.services.documents.apply.dto.apply_document_command import ApplyDocumentCommand, DocumentApplyAction
from contract_costs.services.documents.exeptions import DocumentFatalError
from contract_costs.services.documents.process.dto.process_document_command import ProcessDocumentCommand
from contract_costs.services.documents.process.parse_document_from_file import ParseDocumentFromFileService
from contract_costs.services.documents.scoring.document_decision import DocumentDecision
from contract_costs.services.documents.scoring.document_decision_service import DocumentDecisionService
from contract_costs.services.documents.scoring.simple_scoring_policy import SimpleScoringPolicy
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ProcessDocumentService(ActionHandler[ProcessDocumentCommand, None]):

    def __init__(
        self,
        parse_service: ParseDocumentFromFileService,
        scoring_policy:SimpleScoringPolicy,
        decision_service: DocumentDecisionService,
        apply_service: ApplyDocumentService,
        event_service: BusinessEventService,
    ):
        self._parser = parse_service
        self._scoring_policy = scoring_policy
        self._decision_service = decision_service
        self._apply_service = apply_service
        self._events_service = event_service

    def execute(self, *, action: ProcessDocumentCommand, uow: UnitOfWork) -> None:
        doc_repo = uow.documents
        document = doc_repo.get(
            organization_id=action.organization_id,
            document_id=action.document_id,
        )

        if not document:
            raise ValueError("Document not found")

        if document.parsed_payload is not None and not action.force:
            logger.info("Document already parsed. Use --force to reprocess. Document id: %s", document.id)
            return

        document = document.mark_processing()
        doc_repo.update(document)
        uow.commit()
        logger.info("STATUS BEFORE PARSE: %s", document.document_status)

        if action.force:
            logger.info("Force reprocessing document %s", document.id)

        org_root = cfg.WORK_DIR / str(action.organization_id)
        file_path = org_root / document.file_path

        if document.document_source is None:
            raise RuntimeError("Document source missing")

        try:
            parse_result = self._parser.execute(
                file_path=file_path,
                source=document.document_source,
            )
        except DocumentFatalError as e:
            logger.exception("Fatal parsing error for document %s", document.id)
            try:
                failed_path = DocumentFileOrganizer.move_to_failed(
                    root=org_root,
                    file_path=file_path,
                    reason="parse_error",
                )

                failed = replace(
                    document,
                    file_path=str(failed_path),
                    document_status=DocumentStatus.FAILED,
                )

                doc_repo.update(failed)
                uow.commit()
            except Exception:
                logger.exception("Failed to move document to failed directory")
            raise e

        try:
            raw_path = DocumentFileOrganizer.move_to_raw(
                root=org_root,
                file_path=file_path,
            )
        except Exception:
            logger.exception("Failed to move document to raw directory")
            try:
                failed_path = DocumentFileOrganizer.move_to_failed(
                    root=org_root,
                    file_path=file_path,
                    reason="move_error",
                )

                failed = replace(
                    document,
                    file_path=str(failed_path),
                    document_status=DocumentStatus.FAILED,
                )

                doc_repo.update(failed)
                uow.commit()
            except Exception:
                logger.exception("Failed to move document to failed after move error")
            raise
        logger.info("STATUS BEFORE REPLACE: %s", document.document_status)
        parsed_payload = json.loads(json.dumps(asdict(parse_result), default=self._serialize))
        updated = replace(
            document,
            parsed_payload=parsed_payload,
            document_number=parse_result.record.reference,
            seller_nip=parse_result.seller.tax_number,
            document_type=parse_result.document_type,
            file_path=str(raw_path),
            document_status=DocumentStatus.READY,
            scoring=self._scoring_policy.calculate(
                parsed_payload,
                is_structured_xml=document.document_source == DocumentSource.KSEF)
        )

        doc_repo.update(updated)
        uow.commit()

        decision_result = self._decision_service.decide(
            actor_user_id=action.actor_user_id,
            document=updated,
            uow=uow,
        )
        score = updated.scoring.score if updated.scoring else None
        logger.info(
            "[AUTO-DECISION] doc=%s | score=%s | decision=%s | record_id=%s",
            updated.id,
            score,
            decision_result.decision,
            decision_result.record_id,
        )

        if decision_result.decision == DocumentDecision.AUTO_ATTACH:
            record_id = self._apply_service.execute(
                action=ApplyDocumentCommand(
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                    document_id=updated.id,
                    action=DocumentApplyAction.ADD_TO_EXISTING,
                    target_record_id=decision_result.record_id,
                ),
                uow=uow,
            )
            self._events_service.log(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                level=BusinessEventLevel.INFO,
                message=f"Dokument automatycznie przypięty do istniejącego rekordu. Score {score}",
                entity_type="record",
                entity_id=record_id,
                uow=uow,
            )


        elif decision_result.decision == DocumentDecision.AUTO_CREATE:
            record_id = self._apply_service.execute(
                action=ApplyDocumentCommand(
                    organization_id=action.organization_id,
                    actor_user_id=action.actor_user_id,
                    document_id=updated.id,
                    action=DocumentApplyAction.CREATE_NEW,
                ),
                uow=uow,
            )
            self._events_service.log(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                level=BusinessEventLevel.INFO,
                message=f"Stworzono rekord na bazie dokumentu. Score {score}",
                entity_type="record",
                entity_id=record_id,
                uow=uow,
            )

        else:
            self._events_service.log(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                level=BusinessEventLevel.INFO,
                message=f"Dokument wymaga ręcznej decyzji. Score {score}",
                entity_type="document",
                entity_id=updated.id,
                uow=uow,
            )


    @staticmethod
    def _serialize(obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        return obj
