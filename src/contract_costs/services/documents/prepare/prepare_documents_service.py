import logging

from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentType
from contract_costs.model.financial_record import FinancialRecordStatus, FinancialRecord
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator, EvaluateMode
from contract_costs.services.documents.prepare.dto.candidate_record_dto import CandidateRecordDto
from contract_costs.services.documents.prepare.dto.prepare_document_bundle import PrepareDocumentsBundle
from contract_costs.services.documents.prepare.dto.prepare_document_dto import PreparedDocumentDto

from contract_costs.repository.financial_record_repository import FinancialRecordRepository

logger = logging.getLogger(__name__)

class PrepareDocumentsService:

    def __init__(
        self,
        document_repository: DocumentRepository,
        record_repository: FinancialRecordRepository,
        company_evaluate: CompanyEvaluateOrchestrator,
    ) -> None:
        self._documents = document_repository
        self._records = record_repository
        self._company_evaluate = company_evaluate

    def execute(
        self,
        *,
        organization_id,
        actor_user_id,
    ) -> PrepareDocumentsBundle:

        documents = self._documents.list_unattached(
            organization_id=organization_id,
        )

        prepared: list[PreparedDocumentDto] = []

        for d in documents:

            if d.parsed_payload is None:
                continue

            if d.financial_record_id is not None:
                continue
            candidates =  []
            try:
                candidates = self._find_candidates(
                    organization_id=organization_id,
                    actor_user_id=actor_user_id,
                    seller_nip=d.seller_nip,
                    document_number=d.document_number,
                )

            except RuntimeError:
                logger.warning("Found no candidates for %s, %s",d.document_number, d.seller_nip)

            logger.info("found candidates: %s", candidates)

            if d.document_source is None:
                raise RuntimeError(f"Document {d.id} has no source")

            prepared.append(
                PreparedDocumentDto(
                    document_id=d.id,
                    document_source=d.document_source.value,
                    document_type=d.document_type.value if d.document_type else DocumentType.UNKNOWN.value,
                    document_number=d.document_number,
                    seller_nip=d.seller_nip,
                    file_path=d.file_path,
                    candidates=candidates,
                )
            )

        return PrepareDocumentsBundle(documents=prepared)

    def _find_candidates(
            self,
            *,
            organization_id,
            actor_user_id,
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
            mode=EvaluateMode.NO_CREATE)

        #logger.info("Found Seller: %s", seller)
        records: list[FinancialRecord] = self._records.list_by_seller_id(
            organization_id=organization_id,
            seller_id=seller.id,
        )

        candidates: list[CandidateRecordDto] = []
        records = sorted(
            records,
            key=lambda rr: rr.invoice_date or rr.created_at,
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
