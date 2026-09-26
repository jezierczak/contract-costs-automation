import logging
from decimal import Decimal
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.amount import Amount
from contract_costs.model.company import Company, CompanyVerificationStatus
from contract_costs.model.document import Document
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.documents.query.dto.document_match_dto import (
    CompanySummaryDto,
    DocumentMatchDto,
    DocumentPartyDto,
    MatchCandidateDto,
)
from contract_costs.services.documents.query.dto.get_document_query import GetDocumentQuery
from contract_costs.services.documents.scoring.find_matching_record_service import (
    FindMatchingRecordService,
    MatchResult,
    RecordMatch,
)
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import (
    DocumentParseNormalizer,
)
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import (
    CompanyInput,
    DocumentParseResult,
)
from contract_costs.unit_of_work import UnitOfWork


logger = logging.getLogger(__name__)

MAX_SUGGESTIONS = 5


class GetDocumentQueryService(
    ActionHandler[GetDocumentQuery, DocumentMatchDto]
):
    """Dane ekranu dopasowania dokumentu: kontrahenci (+ podpowiedzi) i kandydaci z powodami."""

    def __init__(
        self,
        matching_service: FindMatchingRecordService,
        company_evaluate: CompanyEvaluateOrchestrator,
        normalizer: DocumentParseNormalizer,
    ) -> None:
        self._matching_service = matching_service
        self._company_evaluate = company_evaluate
        self._normalizer = normalizer

    def execute(self, *, action: GetDocumentQuery, uow: UnitOfWork) -> DocumentMatchDto:
        document = uow.documents.get(
            organization_id=action.organization_id,
            document_id=action.document_id,
        )
        if not document:
            raise ValueError("Document not found")

        parse_result = self._parse(document)
        result = self._matching_service.find(document=document, uow=uow)
        total_gross = (
            Amount.sum([line.amount for line in parse_result.lines]).gross
            if parse_result and parse_result.lines
            else None
        )

        return DocumentMatchDto(
            document_id=document.id,
            document_source=document.document_source.value if document.document_source else None,
            document_type=document.document_type.value if document.document_type else None,
            document_number=document.document_number,
            seller_nip=document.seller_nip,
            file_path=document.file_path,
            confidence_score=document.scoring.score if document.scoring else None,
            confidence_breakdown=document.scoring.breakdown if document.scoring else None,
            invoice_date=parse_result.record.invoice_date if parse_result else None,
            total_gross=total_gross,
            seller=self._party(
                uow=uow, organization_id=action.organization_id,
                data=parse_result.seller if parse_result else None,
                tax_number=result.seller_tax_number, company=result.seller,
            ),
            buyer=self._party(
                uow=uow, organization_id=action.organization_id,
                data=parse_result.buyer if parse_result else None,
                tax_number=result.buyer_tax_number, company=result.buyer,
            ),
            candidates=[
                self._candidate(uow=uow, match=m, result=result, total_gross=total_gross)
                for m in result.matches
            ],
        )

    def _parse(self, document: Document) -> DocumentParseResult | None:
        if not document.parsed_payload:
            return None
        try:
            return self._normalizer.normalize_payload(document.parsed_payload)
        except Exception:
            logger.warning("Cannot normalize payload of document %s", document.id, exc_info=True)
            return None

    def _party(
        self,
        *,
        uow: UnitOfWork,
        organization_id: UUID,
        data: CompanyInput | None,
        tax_number: str | None,
        company: Company | None,
    ) -> DocumentPartyDto:
        suggestions: list[CompanySummaryDto] = []
        if company is None and data is not None:
            suggestions = [
                self._summary(c)
                for c in self._company_evaluate.suggest(uow=uow, organization_id=organization_id, input_=data)
            ][:MAX_SUGGESTIONS]

        return DocumentPartyDto(
            tax_number=tax_number,
            name=data.name if data else None,
            street=data.street if data else None,
            zip_code=data.zip_code if data else None,
            city=data.city if data else None,
            company=self._summary(company) if company else None,
            suggestions=suggestions,
        )

    @staticmethod
    def _summary(company: Company) -> CompanySummaryDto:
        return CompanySummaryDto(
            id=company.id,
            name=company.name,
            tax_number=company.tax_number,
            to_verify=company.verification_status == CompanyVerificationStatus.TO_VERIFY,
        )

    @staticmethod
    def _candidate(
        *,
        uow: UnitOfWork,
        match: RecordMatch,
        result: MatchResult,
        total_gross: Decimal | None,
    ) -> MatchCandidateDto:
        record = match.record
        lines = uow.financial_record_lines.list_by_financial_record(
            organization_id=record.organization_id, financial_record_id=record.id,
        )
        record_total = Amount.sum([line.amount for line in lines]).gross if lines else Decimal("0")
        seller = uow.companies.get(record.seller_id, record.organization_id)
        buyer = uow.companies.get(record.buyer_id, record.organization_id)

        return MatchCandidateDto(
            record_id=record.id,
            reference=record.reference,
            status=record.status.value,
            invoice_date=record.invoice_date,
            total_gross=record_total,
            seller_name=seller.name if seller else None,
            buyer_name=buyer.name if buyer else None,
            reasons=tuple(sorted(r.value for r in match.reasons)),
            same_seller=result.seller is not None and record.seller_id == result.seller.id,
            same_buyer=result.buyer is not None and record.buyer_id == result.buyer.id,
            total_difference=(record_total - total_gross) if total_gross is not None else None,
        )
