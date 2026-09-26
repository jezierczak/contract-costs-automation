import logging
from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable
from uuid import UUID

import contract_costs.config as cfg
from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.model.company import Company, CompanyType
from contract_costs.model.document import Document, DocumentSource
from contract_costs.model.financial_record import FinancialRecord, FinancialRecordStatus
from contract_costs.services.catalogues.record_file_workworkflow_service import RecordFileWorkflowService
from contract_costs.services.common.resolve_utils import normalize_tax_number
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.document_parser import (
    DocumentParser,
)
from contract_costs.services.financial_records.migration.repair_record_companies_command import (
    RepairRecordCompaniesCommand,
)
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class RecordSide(Enum):
    SELLER = "seller"
    BUYER = "buyer"


class RepairKind(Enum):
    FIX = "fix"                              # przepinamy przy --apply
    MISSING_COMPANY = "missing_company"      # brak firmy o NIP-ie z XML
    CONFLICTING_DOCUMENTS = "conflicting"    # pliki XML rekordu podają różne NIP-y
    OWN_COMPANY = "own_company"              # zmiana dotyczy firmy OWN – tylko ręcznie
    UNREADABLE_XML = "unreadable_xml"        # brak pliku / błąd parsowania


@dataclass(frozen=True, slots=True)
class RecordCompanyFix:
    kind: RepairKind
    record_id: UUID
    reference: str
    side: RecordSide | None
    xml_tax_numbers: tuple[str, ...]
    current_company: Company | None
    target_company: Company | None
    detail: str | None = None


class RepairRecordCompaniesService(
    ActionHandler[RepairRecordCompaniesCommand, list[RecordCompanyFix]]
):
    """
    Naprawa rekordów przypiętych do złej firmy przez dawne dopasowanie rozmyte
    (np. faktura SIGNAL wisząca na SIG sp. z o.o.).

    Źródłem prawdy jest plik XML z KSeF, parsowany na nowo parserem KSeF –
    NIP sprzedawcy (Podmiot1) i nabywcy (Podmiot2) porównujemy z firmami rekordu.
    Dokumenty spoza KSeF są pomijane (NIP-y z OCR są niepewne).
    Przepinane są tylko jednoznaczne przypadki (FIX); pozostałe trafiają na listę.
    Bez `apply` tylko zwraca listę.
    """

    def __init__(
        self,
        ksef_parser: DocumentParser,
        file_workflow: RecordFileWorkflowService,
        work_dir: Path | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._parser = ksef_parser
        self._file_workflow = file_workflow
        self._work_dir = work_dir
        self._clock = clock

    def execute(
        self,
        *,
        action: RepairRecordCompaniesCommand,
        uow: UnitOfWork,
    ) -> list[RecordCompanyFix]:
        org_root = (self._work_dir or cfg.WORK_DIR) / str(action.organization_id)

        documents_by_record: dict[UUID, list[Document]] = {}
        for document in uow.documents.list_filtered(
            organization_id=action.organization_id,
            has_record=True,
        ):
            if document.document_source == DocumentSource.KSEF and document.financial_record_id:
                documents_by_record.setdefault(document.financial_record_id, []).append(document)

        fixes: list[RecordCompanyFix] = []
        for record_id, documents in documents_by_record.items():
            record = uow.financial_records.get(organization_id=action.organization_id, record_id=record_id)
            if record is None or record.status == FinancialRecordStatus.DELETED:
                continue

            tax_numbers: dict[RecordSide, set[str]] = {side: set() for side in RecordSide}
            for document in documents:
                try:
                    parsed = self._parser.parse(org_root / document.file_path)
                except Exception as e:
                    logger.warning("Cannot parse KSeF XML %s: %s", document.file_path, e)
                    fixes.append(self._fix(RepairKind.UNREADABLE_XML, record, None, (), None,
                                           detail=f"{document.file_path}: {e}"))
                    continue
                for side, company in ((RecordSide.SELLER, parsed.seller), (RecordSide.BUYER, parsed.buyer)):
                    if nip := normalize_tax_number(company.tax_number):
                        tax_numbers[side].add(nip)

            record_fixes = [
                fix
                for side in RecordSide
                if (fix := self._fix_for(
                    uow=uow, record=record, side=side, tax_numbers=tuple(sorted(tax_numbers[side])),
                )) is not None
            ]
            fixes.extend(record_fixes)

            to_apply = [f for f in record_fixes if f.kind == RepairKind.FIX and f.target_company]
            if action.apply and to_apply:
                for fix in to_apply:
                    field = "seller_id" if fix.side == RecordSide.SELLER else "buyer_id"
                    record = replace(record, **{field: fix.target_company.id})
                record = replace(
                    record,
                    updated_at=self._clock(),
                    updated_by_user_id=action.actor_user_id,
                )
                uow.financial_records.update(record)
                # katalog pliku zależy od nazw firm rekordu
                self._file_workflow.sync(
                    organization_id=action.organization_id,
                    record=record,
                    uow=uow,
                )

        return fixes

    def _fix_for(
        self,
        *,
        uow: UnitOfWork,
        record: FinancialRecord,
        side: RecordSide,
        tax_numbers: tuple[str, ...],
    ) -> RecordCompanyFix | None:
        if not tax_numbers:
            return None

        company_id = record.seller_id if side == RecordSide.SELLER else record.buyer_id
        current = (
            uow.companies.get(organization_id=record.organization_id, company_id=company_id)
            if company_id else None
        )

        if len(tax_numbers) > 1:
            return self._fix(RepairKind.CONFLICTING_DOCUMENTS, record, side, tax_numbers, current)

        nip = tax_numbers[0]
        if current and normalize_tax_number(current.tax_number) == nip:
            return None

        target = uow.companies.get_by_tax_number(tax_number=nip, organization_id=record.organization_id)
        if target is None:
            return self._fix(RepairKind.MISSING_COMPANY, record, side, tax_numbers, current)

        if CompanyType.OWN in {target.role, current.role if current else None}:
            return self._fix(RepairKind.OWN_COMPANY, record, side, tax_numbers, current, target)

        return self._fix(RepairKind.FIX, record, side, tax_numbers, current, target)

    @staticmethod
    def _fix(
        kind: RepairKind,
        record: FinancialRecord,
        side: RecordSide | None,
        tax_numbers: tuple[str, ...],
        current: Company | None,
        target: Company | None = None,
        *,
        detail: str | None = None,
    ) -> RecordCompanyFix:
        return RecordCompanyFix(
            kind=kind,
            record_id=record.id,
            reference=record.reference,
            side=side,
            xml_tax_numbers=tax_numbers,
            current_company=current,
            target_company=target,
            detail=detail,
        )
