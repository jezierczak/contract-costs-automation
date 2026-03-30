import logging
from datetime import datetime
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.company import CompanyType
from contract_costs.model.document import Document
from contract_costs.model.financial_record import FinancialRecordStatus, FinancialRecord
from contract_costs.services.companies.company_evaluate_orchestrator import EvaluateMode, CompanyEvaluateOrchestrator
from contract_costs.services.documents.prepare.dto.candidate_record_dto import CandidateRecordDto
from contract_costs.services.documents.prepare.dto.prepare_document_dto import PreparedDocumentDto
from contract_costs.services.documents.query.dto.get_document_query import GetDocumentQuery
from contract_costs.services.documents.scoring.find_matching_record_service import FindMatchingRecordService, MatchMode
from contract_costs.unit_of_work import UnitOfWork


logger = logging.getLogger(__name__)

class GetDocumentQueryService(
    ActionHandler[GetDocumentQuery, PreparedDocumentDto]
):
    def __init__(
        self,
        company_evaluate: CompanyEvaluateOrchestrator,
        matching_service: FindMatchingRecordService,
    ) -> None:
        self._company_evaluate = company_evaluate
        self._matching_service = matching_service

    def execute(self, *, action, uow):

        repo = uow.documents

        document = repo.get(
            organization_id=action.organization_id,
            document_id=action.document_id,
        )

        if not document:
            raise ValueError("Document not found")

        candidates = []
        try:
            candidates = self._find_candidates(
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                document=document,
                uow=uow
            )

        except RuntimeError:
            logger.warning("Found no candidates for %s, %s", document.document_number, document.seller_nip)


        return PreparedDocumentDto(
            document_id=document.id,
            document_type=document.document_type.value if document.document_type else None,
            document_number=document.document_number,
            document_source=document.document_source.value if document.document_source else None,
            seller_nip=document.seller_nip,
            file_path=document.file_path,
            candidates=candidates,
            confidence_score=document.scoring.score if document.scoring else None,
            confidence_breakdown=document.scoring.breakdown if document.scoring else None,
        )

    def _find_candidates(
            self,
            *,
            document: Document,
            organization_id: UUID,
            actor_user_id: UUID,
            uow: UnitOfWork,
    ) -> list[CandidateRecordDto]:

        matches = self._matching_service.find(
            document=document,
            actor_user_id=actor_user_id,
            uow=uow,
            mode=MatchMode.CANDIDATE
        )

        if not matches:
            return []

        records: list[FinancialRecord] = []

        for record_id in matches:
            record = uow.financial_records.get(
                organization_id=organization_id,
                record_id=record_id
            )

            if record and record.status not in (
                    FinancialRecordStatus.DELETED,
            ):
                records.append(record)

        candidates = [
            CandidateRecordDto(
                record_id=r.id,
                reference=r.reference,
                status=str(r.status.value),
                invoice_date=r.invoice_date,
            )
            for r in records
        ]

        return candidates