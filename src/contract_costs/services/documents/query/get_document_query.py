import logging
from datetime import datetime
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.company import CompanyType
from contract_costs.model.financial_record import FinancialRecordStatus, FinancialRecord
from contract_costs.services.companies.company_evaluate_orchestrator import EvaluateMode, CompanyEvaluateOrchestrator
from contract_costs.services.documents.prepare.dto.candidate_record_dto import CandidateRecordDto
from contract_costs.services.documents.prepare.dto.prepare_document_dto import PreparedDocumentDto
from contract_costs.services.documents.query.dto.get_document_query import GetDocumentQuery
from contract_costs.unit_of_work import UnitOfWork


logger = logging.getLogger(__name__)

class GetDocumentQueryService(
    ActionHandler[GetDocumentQuery, PreparedDocumentDto]
):
    def __init__(
        self,
        company_evaluate: CompanyEvaluateOrchestrator,
    ) -> None:
        self._company_evaluate = company_evaluate

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
                seller_nip=document.seller_nip,
                document_number=document.document_number,
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
            uow:UnitOfWork,
            organization_id:UUID,
            actor_user_id:UUID,
            seller_nip: str | None,
            document_number: str | None,
    ) -> list[CandidateRecordDto]:

        if not seller_nip:
            return []

        seller = self._company_evaluate.evaluate_from_tax(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            input_tax_number=seller_nip,
            role=CompanyType.SELLER,
            mode=EvaluateMode.NO_CREATE,
            uow=uow
        )

        #logger.info("Found Seller: %s", seller)
        records: list[FinancialRecord] = uow.financial_records.list_by_seller_id(
            organization_id=organization_id,
            seller_id=seller.id,
        )

        candidates: list[CandidateRecordDto] = []
        records = sorted(
            records,
            key=lambda rr: (
                datetime.combine(rr.invoice_date, datetime.min.time())
                if rr.invoice_date
                else rr.created_at
            ),
            reverse=True,
        )

        for r in records:

            # opcjonalnie pomijamy zamknięte
            if r.status == FinancialRecordStatus.SENT_TO_ACCOUNTANT or r.status == FinancialRecordStatus.DELETED:
                #logger.info("Skipping record : %s", r)
                continue
            #logger.info("Added record to bundle: %s", r)
            candidates.append(
                CandidateRecordDto(
                    record_id=r.id,
                    reference=r.reference,
                    status=str(r.status.value),
                    invoice_date=r.invoice_date
                )
            )


        return candidates