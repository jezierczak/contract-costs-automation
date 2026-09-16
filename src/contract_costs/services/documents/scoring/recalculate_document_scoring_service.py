import logging
from dataclasses import replace
from uuid import UUID

from contract_costs.model.document import DocumentSource
from contract_costs.services.documents.scoring.simple_scoring_policy import SimpleScoringPolicy
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

class RecalculateDocumentScoringService:

    def __init__(self, scoring_policy: SimpleScoringPolicy):
        self._scoring_policy = scoring_policy

    def execute(self, *, organization_id: UUID, uow: UnitOfWork) -> int:

        documents = uow.documents.list_filtered(
            organization_id=organization_id,
            has_payload=True,
        )

        updated_count = 0

        for document in documents:
            if document.scoring:
                continue
            if not document.parsed_payload:
                logger.debug(
                    "[SCORING] Skipped | doc=%s | no parsed payload",
                    document.id,
                )
                continue
            try:
                scoring = self._scoring_policy.calculate(
                    document.parsed_payload,
                    is_structured_xml = document.document_source == DocumentSource.KSEF
                )

                updated = replace(document, scoring=scoring)

                uow.documents.update(updated)
                updated_count += 1

            except Exception:
                logger.exception(
                    "Failed scoring backfill for doc=%s",
                    document.id,
                )

        uow.commit()

        return updated_count