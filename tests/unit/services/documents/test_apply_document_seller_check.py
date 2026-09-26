from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from contract_costs.model.document import DocumentSource
from contract_costs.services.documents.apply.apply_document_service import (
    ApplyDocumentService,
    SellerMismatchError,
)
from contract_costs.services.documents.apply.dto.apply_document_command import (
    ApplyDocumentCommand,
    DocumentApplyAction,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder

ORG = uuid4()
USER = uuid4()
NOW = datetime(2026, 9, 26, 12, 0)


def _service():
    return ApplyDocumentService(
        create_record_service=MagicMock(),
        file_organizer=MagicMock(),
        file_service=MagicMock(),
        clock=lambda: NOW,
    )


def _setup(uow, *, source=DocumentSource.PDF, document_nip="5532452113"):
    record_seller = CompanyBuilder().with_organization_id(ORG).with_tax_number("6792740424").build()
    document_seller = CompanyBuilder().with_organization_id(ORG).with_tax_number("5532452113").build()
    uow.companies.add(record_seller)
    uow.companies.add(document_seller)
    record = FinancialRecordBuilder().with_organization_id(ORG).with_seller_id(record_seller.id).build()
    uow.financial_records.add(record)
    document = (
        DocumentBuilder()
        .with_organization_id(ORG)
        .with_document_source(source)
        .with_seller_nip(document_nip)
        .build()
    )
    return record, document, document_seller


def _cmd(record, **kwargs):
    return ApplyDocumentCommand(
        organization_id=ORG,
        actor_user_id=USER,
        document_id=uuid4(),
        action=DocumentApplyAction.ADD_TO_EXISTING,
        target_record_id=record.id,
        **kwargs,
    )


def test_seller_mismatch_requires_confirmation(uow):
    record, document, _ = _setup(uow)

    with pytest.raises(SellerMismatchError):
        _service()._check_seller(uow=uow, cmd=_cmd(record), document=document, record=record)


def test_unknown_document_seller_also_requires_confirmation(uow):
    record, document, _ = _setup(uow, document_nip="1234567890")

    with pytest.raises(SellerMismatchError):
        _service()._check_seller(uow=uow, cmd=_cmd(record), document=document, record=record)


def test_confirmed_mismatch_keeps_record_seller(uow):
    record, document, _ = _setup(uow)

    result = _service()._check_seller(
        uow=uow, cmd=_cmd(record, confirm_seller_mismatch=True), document=document, record=record,
    )

    assert result.seller_id == record.seller_id


def test_ksef_document_can_relink_record_seller(uow):
    record, document, document_seller = _setup(uow, source=DocumentSource.KSEF)

    result = _service()._check_seller(
        uow=uow, cmd=_cmd(record, relink_record_seller=True), document=document, record=record,
    )

    assert result.seller_id == document_seller.id
    stored = uow.financial_records.get(organization_id=ORG, record_id=record.id)
    assert stored.seller_id == document_seller.id
    assert stored.updated_by_user_id == USER


def test_ocr_document_cannot_relink_record_seller(uow):
    record, document, _ = _setup(uow)

    with pytest.raises(RuntimeError, match="KSeF"):
        _service()._check_seller(
            uow=uow, cmd=_cmd(record, relink_record_seller=True), document=document, record=record,
        )
