from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

from contract_costs.ksef.parser.ksef_document_parser import KsefDocumentParser
from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentSource
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.services.financial_records.migration.repair_record_companies_command import (
    RepairRecordCompaniesCommand,
)
from contract_costs.services.financial_records.migration.repair_record_companies_service import (
    RecordSide,
    RepairKind,
    RepairRecordCompaniesService,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder

ORG = uuid4()
USER = uuid4()
NOW = datetime(2026, 9, 26, 12, 0)
NS = "http://crd.gov.pl/wzor/2025/06/25/13775/"

OWN_NIP = "1111111111"
SIG_NIP = "5251234560"
SIGNAL_NIP = "7812345678"


def _ksef_xml(*, seller_nip: str, buyer_nip: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<k:Root xmlns:k="{NS}">
  <k:Fa>
    <k:RodzajFaktury>VAT</k:RodzajFaktury>
    <k:P_2>FV/1/2026</k:P_2>
    <k:P_1>2026-02-10T00:00:00Z</k:P_1>
    <k:KodWaluty>PLN</k:KodWaluty>
    <k:P_13_1>100.00</k:P_13_1>
    <k:P_14_1>23.00</k:P_14_1>
    <k:P_15>123.00</k:P_15>
  </k:Fa>
  <k:Podmiot1><k:DaneIdentyfikacyjne><k:Nazwa>Seller</k:Nazwa><k:NIP>{seller_nip}</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot1>
  <k:Podmiot2><k:DaneIdentyfikacyjne><k:Nazwa>Buyer</k:Nazwa><k:NIP>{buyer_nip}</k:NIP></k:DaneIdentyfikacyjne></k:Podmiot2>
  <k:FaWiersz>
    <k:P_7>Usluga</k:P_7>
    <k:P_8B>1</k:P_8B>
    <k:P_11>100.00</k:P_11>
    <k:P_12>23</k:P_12>
  </k:FaWiersz>
</k:Root>"""


def _company(uow, nip, name, role=CompanyType.SUPPLIER):
    company = (
        CompanyBuilder()
        .with_organization_id(ORG)
        .with_tax_number(nip)
        .with_name(name)
        .with_role(role)
        .build()
    )
    uow.companies.add(company)
    return company


def _record_with_document(
    uow, tmp_path: Path, *, seller, buyer, xml: str | None,
    source=DocumentSource.KSEF, status=None,
):
    builder = (
        FinancialRecordBuilder()
        .with_organization_id(ORG)
        .with_seller_id(seller.id)
        .with_buyer_id(buyer.id)
    )
    if status is not None:
        builder = builder.with_status(status)
    record = builder.build()
    uow.financial_records.add(record)

    relative = f"records/{record.id}.xml"
    if xml is not None:
        path = tmp_path / str(ORG) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(xml, encoding="utf-8")

    uow.documents.add(
        DocumentBuilder()
        .with_organization_id(ORG)
        .with_financial_record_id(record.id)
        .with_document_source(source)
        .with_file_path(relative)
        .build()
    )
    return record


def _run(uow, tmp_path, *, apply=False, file_workflow=None):
    service = RepairRecordCompaniesService(
        ksef_parser=KsefDocumentParser(),
        file_workflow=file_workflow or MagicMock(),
        work_dir=tmp_path,
        clock=lambda: NOW,
    )
    return service.execute(
        action=RepairRecordCompaniesCommand(organization_id=ORG, actor_user_id=USER, apply=apply),
        uow=uow,
    )


def test_dry_run_lists_record_linked_to_wrong_seller(uow, tmp_path):
    own = _company(uow, OWN_NIP, "OWN", CompanyType.OWN)
    sig = _company(uow, SIG_NIP, "SIG SP. Z O.O.")
    signal = _company(uow, SIGNAL_NIP, "SIGNAL SP. Z O.O.")
    record = _record_with_document(
        uow, tmp_path, seller=signal, buyer=own,
        xml=_ksef_xml(seller_nip=SIG_NIP, buyer_nip=OWN_NIP),
    )

    fixes = _run(uow, tmp_path)

    assert [(f.kind, f.side, f.current_company.id, f.target_company.id) for f in fixes] == [
        (RepairKind.FIX, RecordSide.SELLER, signal.id, sig.id),
    ]
    assert uow.financial_records.get(organization_id=ORG, record_id=record.id).seller_id == signal.id


def test_apply_relinks_record_and_syncs_files(uow, tmp_path):
    own = _company(uow, OWN_NIP, "OWN", CompanyType.OWN)
    sig = _company(uow, SIG_NIP, "SIG SP. Z O.O.")
    signal = _company(uow, SIGNAL_NIP, "SIGNAL SP. Z O.O.")
    record = _record_with_document(
        uow, tmp_path, seller=signal, buyer=own,
        xml=_ksef_xml(seller_nip=SIG_NIP, buyer_nip=OWN_NIP),
    )
    file_workflow = MagicMock()

    _run(uow, tmp_path, apply=True, file_workflow=file_workflow)

    stored = uow.financial_records.get(organization_id=ORG, record_id=record.id)
    assert stored.seller_id == sig.id
    assert stored.buyer_id == own.id
    assert stored.updated_by_user_id == USER
    file_workflow.sync.assert_called_once()
    assert file_workflow.sync.call_args.kwargs["record"].seller_id == sig.id


def test_matching_record_is_not_listed(uow, tmp_path):
    own = _company(uow, OWN_NIP, "OWN", CompanyType.OWN)
    sig = _company(uow, SIG_NIP, "SIG SP. Z O.O.")
    _record_with_document(
        uow, tmp_path, seller=sig, buyer=own,
        xml=_ksef_xml(seller_nip=SIG_NIP, buyer_nip=OWN_NIP),
    )

    assert _run(uow, tmp_path) == []


def test_non_ksef_documents_are_skipped(uow, tmp_path):
    own = _company(uow, OWN_NIP, "OWN", CompanyType.OWN)
    _company(uow, SIG_NIP, "SIG SP. Z O.O.")
    signal = _company(uow, SIGNAL_NIP, "SIGNAL SP. Z O.O.")
    _record_with_document(
        uow, tmp_path, seller=signal, buyer=own,
        xml=_ksef_xml(seller_nip=SIG_NIP, buyer_nip=OWN_NIP),
        source=DocumentSource.PDF,
    )

    assert _run(uow, tmp_path) == []


def test_deleted_records_are_skipped(uow, tmp_path):
    own = _company(uow, OWN_NIP, "OWN", CompanyType.OWN)
    _company(uow, SIG_NIP, "SIG SP. Z O.O.")
    signal = _company(uow, SIGNAL_NIP, "SIGNAL SP. Z O.O.")
    _record_with_document(
        uow, tmp_path, seller=signal, buyer=own,
        xml=_ksef_xml(seller_nip=SIG_NIP, buyer_nip=OWN_NIP),
        status=FinancialRecordStatus.DELETED,
    )

    assert _run(uow, tmp_path) == []


def test_missing_company_is_only_listed(uow, tmp_path):
    own = _company(uow, OWN_NIP, "OWN", CompanyType.OWN)
    signal = _company(uow, SIGNAL_NIP, "SIGNAL SP. Z O.O.")
    record = _record_with_document(
        uow, tmp_path, seller=signal, buyer=own,
        xml=_ksef_xml(seller_nip=SIG_NIP, buyer_nip=OWN_NIP),
    )

    fixes = _run(uow, tmp_path, apply=True)

    assert [f.kind for f in fixes] == [RepairKind.MISSING_COMPANY]
    assert uow.financial_records.get(organization_id=ORG, record_id=record.id).seller_id == signal.id


def test_change_involving_own_company_is_only_listed(uow, tmp_path):
    own = _company(uow, OWN_NIP, "OWN", CompanyType.OWN)
    other_own = _company(uow, "2222222222", "OWN 2", CompanyType.OWN)
    sig = _company(uow, SIG_NIP, "SIG SP. Z O.O.")
    record = _record_with_document(
        uow, tmp_path, seller=sig, buyer=own,
        xml=_ksef_xml(seller_nip=SIG_NIP, buyer_nip="2222222222"),
    )

    fixes = _run(uow, tmp_path, apply=True)

    assert [(f.kind, f.side, f.target_company.id) for f in fixes] == [
        (RepairKind.OWN_COMPANY, RecordSide.BUYER, other_own.id),
    ]
    assert uow.financial_records.get(organization_id=ORG, record_id=record.id).buyer_id == own.id


def test_missing_xml_file_is_reported(uow, tmp_path):
    own = _company(uow, OWN_NIP, "OWN", CompanyType.OWN)
    sig = _company(uow, SIG_NIP, "SIG SP. Z O.O.")
    _record_with_document(uow, tmp_path, seller=sig, buyer=own, xml=None)

    fixes = _run(uow, tmp_path)

    assert [(f.kind, f.side) for f in fixes] == [(RepairKind.UNREADABLE_XML, None)]
