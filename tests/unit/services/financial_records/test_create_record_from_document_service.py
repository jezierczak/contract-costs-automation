from datetime import date
from decimal import Decimal
import json
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentType
from contract_costs.model.financial_record import (
    FinancialRecordStatus,
    PaymentMethod,
    PaymentStatus,
)
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.amount import Amount, AmountInputType, VatRate
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import (
    InvoiceCommand,
)
from contract_costs.services.financial_records.assigment.invoice_sources.document.create_record_from_document_service import (
    CreateRecordFromDocumentService,
)
from contract_costs.services.financial_records.assigment.invoice_sources.document.dto.create_record_from_document_command import (
    CreateRecordFromDocumentCommand,
)
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import (
    DocumentParseNormalizer,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    FinancialRecordLineUpdate,
    FinancialRecordUpdate,
)
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import (
    CompanyInput,
    DocumentParseResult,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder


RAW_OCR_PAYLOAD_1 = """
"{""buyer"": {""city"": ""Kraków"", ""name"": ""REMONTIVO SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ"", ""role"": ""Buyer"", ""email"": null, ""state"": ""MAŁOPOLSKIE"", ""street"": ""Rynek Główny 28"", ""country"": ""POLSKA"", ""zip_code"": ""31-010"", ""tax_number"": ""6762680195"", ""bank_account"": null, ""phone_number"": null}, ""lines"": [{""unit"": ""szt"", ""amount"": {""value"": ""88.0"", ""vat_rate"": ""0.23"", ""tax_treatment"": ""tax_deductible""}, ""quantity"": ""2"", ""item_name"": ""PIANA PISTOLETOWA OGNIOCHRONNA PREFIX B1 750ML (12SZT/OPAK) DEN"", ""description"": null, ""contract_code"": null, ""agreement_code"": null, ""record_line_id"": null, ""value_type_code"": null, ""record_reference"": null, ""contract_node_code"": null, ""agreement_node_code"": null}, {""unit"": ""m2"", ""amount"": {""value"": ""32.4"", ""vat_rate"": ""0.23"", ""tax_treatment"": ""tax_deductible""}, ""quantity"": ""2.4"", ""item_name"": ""PŁYTA GIPS IMPREGN. 12.5/1200/2000 (66SZT/PAL) SIN"", ""description"": null, ""contract_code"": null, ""agreement_code"": null, ""record_line_id"": null, ""value_type_code"": null, ""record_reference"": null, ""contract_node_code"": null, ""agreement_node_code"": null}, {""unit"": ""szt"", ""amount"": {""value"": ""33.15"", ""vat_rate"": ""0.23"", ""tax_treatment"": ""tax_deductible""}, ""quantity"": ""1"", ""item_name"": ""TAŚMA TYNKARSKA NA POW. CHROPOWATE POMARAŃCZOWA DT_PRO 48MM/50M (24SZT/OPAK) BDT"", ""description"": null, ""contract_code"": null, ""agreement_code"": null, ""record_line_id"": null, ""value_type_code"": null, ""record_reference"": null, ""contract_node_code"": null, ""agreement_node_code"": null}, {""unit"": ""szt"", ""amount"": {""value"": ""65.34"", ""vat_rate"": ""0.23"", ""tax_treatment"": ""tax_deductible""}, ""quantity"": ""1"", ""item_name"": ""TEKTURA FALISTA KARBOWANA 1/25M PREFIX SIT"", ""description"": null, ""contract_code"": null, ""agreement_code"": null, ""record_line_id"": null, ""value_type_code"": null, ""record_reference"": null, ""contract_node_code"": null, ""agreement_node_code"": null}, {""unit"": ""szt"", ""amount"": {""value"": ""189.28"", ""vat_rate"": ""0.23"", ""tax_treatment"": ""tax_deductible""}, ""quantity"": ""4"", ""item_name"": ""TEKTURA MALARSKA LITA 1/20M PREFIX SIT"", ""description"": null, ""contract_code"": null, ""agreement_code"": null, ""record_line_id"": null, ""value_type_code"": null, ""record_reference"": null, ""contract_node_code"": null, ""agreement_node_code"": null}, {""unit"": ""szt"", ""amount"": {""value"": ""173.4"", ""vat_rate"": ""0.23"", ""tax_treatment"": ""tax_deductible""}, ""quantity"": ""2"", ""item_name"": ""ZAPRAWA DO NAPRAW GEOLITE 40 25KG KER"", ""description"": null, ""contract_code"": null, ""agreement_code"": null, ""record_line_id"": null, ""value_type_code"": null, ""record_reference"": null, ""contract_node_code"": null, ""agreement_node_code"": null}], ""record"": {""tags"": null, ""status"": ""draft"", ""command"": ""APPLY"", ""due_date"": ""2026-02-16"", ""paid_date"": null, ""record_id"": null, ""reference"": ""ZFS-KA1B2600572"", ""invoice_date"": ""2026-02-16"", ""selling_date"": ""2026-02-16"", ""old_reference"": null, ""payment_method"": ""card"", ""payment_status"": ""unknown"", ""buyer_tax_number"": null, ""seller_tax_number"": null}, ""seller"": {""city"": ""Kraków"", ""name"": ""SIG Spółka z o.o. Oddział SIG Ruda Śląska"", ""role"": ""Seller"", ""email"": null, ""state"": null, ""street"": ""ul. Kamieńskiego 51"", ""country"": ""POLSKA"", ""zip_code"": ""30-644"", ""tax_number"": ""6792740424"", ""bank_account"": ""PL65103011880000000059830200"", ""phone_number"": ""+48 32 203 66 25""}, ""document_type"": ""invoice""}"
"""

RAW_OCR_PAYLOAD_2 = """
"{""buyer"": {""city"": ""Kraków"", ""name"": ""Renontivo Spółka z Ograni czoną Odpowiedzialnością"", ""role"": ""Buyer"", ""email"": null, ""state"": null, ""street"": ""ul. Rynek Główny 28"", ""country"": null, ""zip_code"": ""31-010"", ""tax_number"": ""6762680195"", ""bank_account"": null, ""phone_number"": null}, ""lines"": [], ""record"": {""tags"": null, ""status"": ""draft"", ""command"": ""APPLY"", ""due_date"": null, ""paid_date"": null, ""record_id"": null, ""reference"": ""000313/2026"", ""invoice_date"": ""2026-02-14"", ""selling_date"": ""2026-02-14"", ""old_reference"": null, ""payment_method"": ""cash"", ""payment_status"": ""paid"", ""buyer_tax_number"": null, ""seller_tax_number"": null}, ""seller"": {""city"": ""JAWORZNO"", ""name"": ""\\""CANDIA\\"" K.JELEN SPÓŁKA JAWNA"", ""role"": ""Seller"", ""email"": null, ""state"": null, ""street"": ""UL. GRUNWALDZKA 275A"", ""country"": null, ""zip_code"": ""43-603"", ""tax_number"": ""6321001207"", ""bank_account"": ""37 1050 1360 1000 0090 3016 7754"", ""phone_number"": null}, ""document_type"": ""invoice""}"
"""

RAW_OCR_PAYLOAD_3 = """
"{""buyer"": {""city"": ""KRAKÓW"", ""name"": ""REMONTIVO SPÓŁKA ZOO."", ""role"": ""Buyer"", ""email"": null, ""state"": null, ""street"": ""RYNEK GŁÓWNY, 28"", ""country"": null, ""zip_code"": ""31-010"", ""tax_number"": ""6762680195"", ""bank_account"": null, ""phone_number"": null}, ""lines"": [{""unit"": ""szt"", ""amount"": {""value"": ""6900"", ""vat_rate"": ""0.23"", ""tax_treatment"": ""tax_deductible""}, ""quantity"": ""1000"", ""item_name"": ""RĘKAWICE NAKRAPIANE 97-"", ""description"": null, ""contract_code"": null, ""agreement_code"": null, ""record_line_id"": null, ""value_type_code"": null, ""record_reference"": null, ""contract_node_code"": null, ""agreement_node_code"": null}, {""unit"": ""m"", ""amount"": {""value"": ""3577"", ""vat_rate"": ""0.23"", ""tax_treatment"": ""tax_deductible""}, ""quantity"": ""1009"", ""item_name"": ""ŁZADLO DO ZAPRAW 3DS"", ""description"": null, ""contract_code"": null, ""agreement_code"": null, ""record_line_id"": null, ""value_type_code"": null, ""record_reference"": null, ""contract_node_code"": null, ""agreement_node_code"": null}], ""record"": {""tags"": null, ""status"": ""draft"", ""command"": ""APPLY"", ""due_date"": null, ""paid_date"": null, ""record_id"": null, ""reference"": ""442026/006/8345"", ""invoice_date"": ""2026-02-16"", ""selling_date"": ""2026-02-16"", ""old_reference"": null, ""payment_method"": ""cash"", ""payment_status"": ""unknown"", ""buyer_tax_number"": null, ""seller_tax_number"": null}, ""seller"": {""city"": ""Warszawa"", ""name"": ""Bricoman Polska Sp. z o.o."", ""role"": ""Seller"", ""email"": ""jaworzno@yDricoman pi"", ""state"": null, ""street"": ""ul Murmańska 25"", ""country"": null, ""zip_code"": ""04-203"", ""tax_number"": ""1132568413"", ""bank_account"": ""22 1050 0086 1000 0090 3035 9435"", ""phone_number"": null}, ""document_type"": ""proforma""}"
"""

RAW_OCR_PAYLOAD_4 = """
{"buyer": {"city": null, "name": null, "role": "Buyer", "email": null, "state": null, "street": null, "country": null, "zip_code": null, "tax_number": "62680195", "bank_account": null, "phone_number": null}, "lines": [{"unit": "unknown", "amount": {"value": "18.04", "vat_rate": "0.23", "tax_treatment": "tax_deductible"}, "quantity": "0.41", "item_name": "WKRET SAKUW DO KE", "contract_id": null, "description": null, "record_line_id": null, "value_type_code": null, "contract_node_id": null, "record_reference": null}, {"unit": "unknown", "amount": {"value": "67.98", "vat_rate": "0.23", "tax_treatment": "tax_deductible"}, "quantity": "2", "item_name": "LISTWA ŁL L OWH A", "contract_id": null, "description": null, "record_line_id": null, "value_type_code": null, "contract_node_id": null, "record_reference": null}], "record": {"tags": null, "status": "draft", "command": "APPLY", "due_date": null, "paid_date": "2026-02-13", "record_id": null, "reference": "AI-c88fc6b55602", "invoice_date": "2026-02-13", "selling_date": null, "old_reference": null, "payment_method": "card", "payment_status": "paid", "buyer_tax_number": null, "seller_tax_number": null}, "seller": {"city": "Strzelce Upolskie", "name": null, "role": "Seller", "email": null, "state": null, "street": "ul 5luuowa IA", "country": null, "zip_code": "41 tW6", "tax_number": "781190944", "bank_account": null, "phone_number": null}, "document_type": "receipt"}
"""


def _payload_dict(raw_payload: str) -> dict:
    content = raw_payload.strip()
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1]
        content = content.replace('""', '"')
    return json.loads(content)


def _make_parse_result() -> DocumentParseResult:
    record = FinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/1/2026",
        record_id=None,
        old_reference=None,
        invoice_date=date(2026, 2, 10),
        selling_date=date(2026, 2, 10),
        buyer_tax_number="1111111111",
        seller_tax_number="2222222222",
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=date(2026, 2, 20),
        paid_date=None,
        tags=None,
        payment_status=PaymentStatus.UNPAID,
        status=FinancialRecordStatus.DRAFT,
    )
    line = FinancialRecordLineUpdate(
        record_line_id=None,
        record_reference=None,
        item_name="Pozycja",
        description=None,
        quantity=Decimal("1"),
        unit=UnitOfMeasure.PIECE,
        amount=Amount(value=Decimal("100"), input_type=AmountInputType.NET, vat_rate=VatRate.VAT_23),
        contract_reference=None,
        contract_node_reference=None,
        value_type_reference=None,
        agreement_reference=None,
        agreement_node_reference=None
    )
    buyer = CompanyInput(
        name="Buyer",
        tax_number="1111111111",
        street=None,
        city=None,
        state=None,
        zip_code=None,
        country=None,
        phone_number=None,
        email=None,
        bank_account=None,
        role=CompanyType.OWN.value,
    )
    seller = CompanyInput(
        name="Seller",
        tax_number="2222222222",
        street=None,
        city=None,
        state=None,
        zip_code=None,
        country=None,
        phone_number=None,
        email=None,
        bank_account=None,
        role=CompanyType.SUPPLIER.value,
    )
    return DocumentParseResult(
        document_type=DocumentType.INVOICE,
        record=record,
        lines=[line],
        buyer=buyer,
        seller=seller,
    )


def test_execute_raises_when_document_has_no_payload(document_repo, uow):
    service = CreateRecordFromDocumentService(
        company_evaluate=MagicMock(),
        normalizer=MagicMock(),
        ingest_orchestrator=MagicMock(),
        record_file_organizer=MagicMock(),
        file_workflow=MagicMock(),
    )
    document = DocumentBuilder().with_parsed_payload(None).build()
    document_repo.add(document)

    with pytest.raises(RuntimeError, match="no parsed payload"):
        service.execute(
            action=CreateRecordFromDocumentCommand(
                organization_id=document.organization_id,
                actor_user_id=uuid4(),
                document=document,
                override_reference=None,
                override_seller_nip=None,
                override_document_type=None,
            ),
            uow=uow
        )


def test_execute_creates_record_attaches_document_and_syncs():
    organization_id = uuid4()
    actor_user_id = uuid4()
    new_record_id = uuid4()

    normalizer = MagicMock()
    normalizer.normalize_payload.return_value = _make_parse_result()
    company_evaluate = MagicMock()
    buyer = CompanyBuilder().with_role(CompanyType.OWN).with_is_active(True).build()
    seller = CompanyBuilder().with_role(CompanyType.SUPPLIER).with_is_active(True).build()
    company_evaluate.evaluate.side_effect = [buyer, seller]

    ingest = MagicMock()
    ingest.execute.return_value = new_record_id

    document_repo = MagicMock()
    record = FinancialRecordBuilder().with_organization_id(organization_id).with_id(new_record_id).build()
    record_repo = MagicMock()
    record_repo.get.return_value = record
    file_workflow = MagicMock()

    service = CreateRecordFromDocumentService(
        company_evaluate=company_evaluate,
        normalizer=normalizer,
        ingest_orchestrator=ingest,
        record_file_organizer=MagicMock(),
        file_workflow=file_workflow,
    )

    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_parsed_payload({"parsed": True})
        .build()
    )
    document_repo.get.return_value = document
    uow = MagicMock()
    uow.documents = document_repo
    uow.financial_records = record_repo
    result = service.execute(
        action=CreateRecordFromDocumentCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            document=document,
            override_reference="FV/OVERRIDE",
            override_seller_nip="9999999999",
            override_document_type=DocumentType.CORRECTION,
        ),
        uow=uow
    )

    assert result == new_record_id
    ingest.execute.assert_called_once()
    batch = ingest.execute.call_args.kwargs["action"].batch
    assert batch.financial_records[0].reference == "FV/OVERRIDE"
    assert batch.financial_records[0].status == FinancialRecordStatus.NEW_COST
    assert batch.lines[0].record_reference == "FV/OVERRIDE"

    # second evaluate call = seller with override nip
    second_eval_input = company_evaluate.evaluate.call_args_list[1].kwargs["input_"]
    assert second_eval_input.tax_number == "9999999999"

    document_repo.attach_to_record.assert_called_once_with(
        organization_id=organization_id,
        document_id=document.id,
        record_id=new_record_id,
    )
    file_workflow.sync.assert_called_once_with(
        organization_id=organization_id,
        record=record,
        uow=uow,
    )


@pytest.mark.parametrize(
    ("raw_payload", "expected_line_count", "expected_reference"),
    [
        (RAW_OCR_PAYLOAD_1, 6, "ZFS-KA1B2600572"),
        (RAW_OCR_PAYLOAD_2, 0, "000313/2026"),
        (RAW_OCR_PAYLOAD_3, 2, "442026/006/8345"),
        (RAW_OCR_PAYLOAD_4, 2, "AI-c88fc6b55602"),
    ],
)
def test_execute_parses_real_ocr_payloads_inmemory(
    raw_payload,
    expected_line_count,
    expected_reference,
    uow,
    document_repo,
):
    organization_id = uuid4()
    actor_user_id = uuid4()
    new_record_id = uuid4()

    payload = _payload_dict(raw_payload)
    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_parsed_payload(payload)
        .build()
    )
    document_repo.add(document)

    buyer = (
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.OWN)
        .with_is_active(True)
        .build()
    )
    seller = (
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.SUPPLIER)
        .with_is_active(True)
        .build()
    )
    company_evaluate = MagicMock()
    company_evaluate.evaluate.side_effect = [buyer, seller]

    ingest = MagicMock()
    ingest.execute.return_value = new_record_id

    service = CreateRecordFromDocumentService(
        company_evaluate=company_evaluate,
        normalizer=DocumentParseNormalizer(),
        ingest_orchestrator=ingest,
        record_file_organizer=MagicMock(),
        file_workflow=MagicMock(),
    )

    result = service.execute(
        action=CreateRecordFromDocumentCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            document=document,
            override_reference=None,
            override_seller_nip=None,
            override_document_type=None,
        ),
        uow=uow,
    )

    assert result == new_record_id

    batch = ingest.execute.call_args.kwargs["action"].batch
    assert len(batch.lines) == expected_line_count
    assert batch.financial_records[0].reference == expected_reference
    assert batch.financial_records[0].status == FinancialRecordStatus.NEW_COST

    stored_doc = document_repo.get(
        organization_id=organization_id,
        document_id=document.id,
    )
    assert stored_doc is not None
    assert stored_doc.financial_record_id == new_record_id


def test_execute_generates_reference_placeholder_when_missing_in_ocr_payload(uow, document_repo):
    organization_id = uuid4()
    actor_user_id = uuid4()
    new_record_id = uuid4()

    payload = _payload_dict(RAW_OCR_PAYLOAD_1)
    payload["record"]["reference"] = "   "

    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_parsed_payload(payload)
        .build()
    )
    document_repo.add(document)

    service = CreateRecordFromDocumentService(
        company_evaluate=MagicMock(
            evaluate=MagicMock(
                side_effect=[
                    CompanyBuilder()
                    .with_organization_id(organization_id)
                    .with_role(CompanyType.OWN)
                    .build(),
                    CompanyBuilder()
                    .with_organization_id(organization_id)
                    .with_role(CompanyType.SUPPLIER)
                    .build(),
                ]
            )
        ),
        normalizer=DocumentParseNormalizer(),
        ingest_orchestrator=MagicMock(execute=MagicMock(return_value=new_record_id)),
        record_file_organizer=MagicMock(),
        file_workflow=MagicMock(),
    )

    result = service.execute(
        action=CreateRecordFromDocumentCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            document=document,
            override_reference=None,
            override_seller_nip=None,
            override_document_type=None,
        ),
        uow=uow,
    )
    assert result == new_record_id
    batch = service._ingest.execute.call_args.kwargs["action"].batch
    assert batch.financial_records[0].reference.startswith("AI-")


def test_execute_returns_placeholder_companies_when_buyer_seller_missing_data(uow, document_repo):
    organization_id = uuid4()
    actor_user_id = uuid4()
    new_record_id = uuid4()
    payload = {
        "buyer": {},
        "seller": {},
        "record": {
            "reference": "OCR-PLACEHOLDER-1",
            "invoice_date": "2026-02-16",
            "selling_date": "2026-02-16",
            "payment_method": "cash",
            "payment_status": "unknown",
        },
        "lines": [],
        "document_type": "invoice",
    }
    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_parsed_payload(payload)
        .build()
    )
    document_repo.add(document)

    def _evaluate_with_placeholder(**kwargs):
        input_ = kwargs["input_"]
        role = CompanyType(input_.role)
        name = input_.name or f"PLACEHOLDER-{uuid4().hex[:8]}"
        tax_number = input_.tax_number or f"TMP-{uuid4().hex[:8]}"
        return (
            CompanyBuilder()
            .with_organization_id(organization_id)
            .with_role(role)
            .with_name(name)
            .with_tax_number(tax_number)
            .build()
        )

    company_evaluate = MagicMock()
    company_evaluate.evaluate.side_effect = _evaluate_with_placeholder
    ingest = MagicMock()
    ingest.execute.return_value = new_record_id

    service = CreateRecordFromDocumentService(
        company_evaluate=company_evaluate,
        normalizer=DocumentParseNormalizer(),
        ingest_orchestrator=ingest,
        record_file_organizer=MagicMock(),
        file_workflow=MagicMock(),
    )

    result = service.execute(
        action=CreateRecordFromDocumentCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            document=document,
            override_reference=None,
            override_seller_nip=None,
            override_document_type=None,
        ),
        uow=uow,
    )
    assert result == new_record_id
    batch = ingest.execute.call_args.kwargs["action"].batch
    assert batch.financial_records[0].buyer.name.startswith("PLACEHOLDER-")
    assert batch.financial_records[0].seller.name.startswith("PLACEHOLDER-")
    assert batch.financial_records[0].buyer.tax_number.startswith("TMP-")
    assert batch.financial_records[0].seller.tax_number.startswith("TMP-")
    assert batch.financial_records[0].buyer.role == CompanyType.BUYER
    assert batch.financial_records[0].seller.role == CompanyType.SELLER
    assert batch.lines == []


def test_execute_does_not_crash_for_heavily_corrupted_payload_and_keeps_empty_lines(uow, document_repo):
    organization_id = uuid4()
    actor_user_id = uuid4()
    new_record_id = uuid4()
    payload = {
        "buyer": None,
        "seller": "broken",
        "record": {
            "reference": "",
            "invoice_date": "bad-date",
            "selling_date": "bad-date",
            "payment_method": "???",
            "payment_status": "???",
        },
        "lines": "totally-wrong",
        "document_type": "unknown",
    }
    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_parsed_payload(payload)
        .build()
    )
    document_repo.add(document)

    company_evaluate = MagicMock()
    company_evaluate.evaluate.side_effect = [
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.BUYER)
        .with_name("PLACEHOLDER-BUYER")
        .with_tax_number("TMP-BUYER")
        .build(),
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.SELLER)
        .with_name("PLACEHOLDER-SELLER")
        .with_tax_number("TMP-SELLER")
        .build(),
    ]
    ingest = MagicMock()
    ingest.execute.return_value = new_record_id

    service = CreateRecordFromDocumentService(
        company_evaluate=company_evaluate,
        normalizer=DocumentParseNormalizer(),
        ingest_orchestrator=ingest,
        record_file_organizer=MagicMock(),
        file_workflow=MagicMock(),
    )

    result = service.execute(
        action=CreateRecordFromDocumentCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            document=document,
            override_reference=None,
            override_seller_nip=None,
            override_document_type=None,
        ),
        uow=uow,
    )
    assert result == new_record_id
    batch = ingest.execute.call_args.kwargs["action"].batch
    assert batch.financial_records[0].reference.startswith("AI-")
    assert batch.lines == []


def test_execute_normalizes_invalid_line_values_to_safe_defaults_inmemory(uow, document_repo):
    organization_id = uuid4()
    actor_user_id = uuid4()
    new_record_id = uuid4()

    payload = _payload_dict(RAW_OCR_PAYLOAD_4)
    payload["lines"][0]["unit"] = "???"
    payload["lines"][0]["quantity"] = "not-a-number"
    payload["lines"][0]["amount"]["value"] = "bad"
    payload["record"]["payment_method"] = "not-known"
    payload["record"]["payment_status"] = "not-known"

    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_parsed_payload(payload)
        .build()
    )
    document_repo.add(document)

    buyer = (
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.OWN)
        .with_is_active(True)
        .build()
    )
    seller = (
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.SUPPLIER)
        .with_is_active(True)
        .build()
    )
    company_evaluate = MagicMock()
    company_evaluate.evaluate.side_effect = [buyer, seller]

    ingest = MagicMock()
    ingest.execute.return_value = new_record_id

    service = CreateRecordFromDocumentService(
        company_evaluate=company_evaluate,
        normalizer=DocumentParseNormalizer(),
        ingest_orchestrator=ingest,
        record_file_organizer=MagicMock(),
        file_workflow=MagicMock(),
    )

    service.execute(
        action=CreateRecordFromDocumentCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            document=document,
            override_reference=None,
            override_seller_nip=None,
            override_document_type=None,
        ),
        uow=uow,
    )

    batch = ingest.execute.call_args.kwargs["action"].batch
    first_line = batch.lines[0]
    assert first_line.quantity == Decimal("1")
    assert first_line.amount.value == Decimal("0.00")
    assert first_line.unit == UnitOfMeasure.PIECE
    assert batch.financial_records[0].payment_method == PaymentMethod.UNKNOWN
    assert batch.financial_records[0].payment_status == PaymentStatus.UNKNOWN
