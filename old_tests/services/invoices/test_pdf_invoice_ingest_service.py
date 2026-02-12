import pytest
from uuid import UUID, uuid4

from contract_costs.model.financial_record import FinancialRecordStatus, PaymentMethod, PaymentStatus
from contract_costs.repository.inmemory.financial_record_repository import InMemoryFinancialRecordRepository
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.financial_records.assigment.ingest.pdf_financial_record_ingest_service import (
    PdfFinancialRecordIngestService,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    ResolvedFinancialRecordUpdate,
)
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_ref_result import (
    RecordApplyAction,
)


def test_pdf_ingest_creates_invoice(invoice_repo,pdf_ingest_service,owner_company,client_company) -> None:
    # -------------------------------------------------
    # GIVEN
    # -------------------------------------------------
    repo = invoice_repo
    service = pdf_ingest_service

    update = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/01/2024",
        record_id=None,
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.UNKNOWN,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNKNOWN,
        status=FinancialRecordStatus.NEW_COST,
        scan_filename="raw/FV01.pdf",
        tags=None,
    )

    # -------------------------------------------------
    # WHEN
    # -------------------------------------------------
    ref_map = service.apply([update])

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert "FV/01/2024" in ref_map

    ref = ref_map["FV/01/2024"]
    assert ref.action == RecordApplyAction.APPLIED
    assert isinstance(ref.record_id, UUID)

    invoice = repo.get(ref.record_id)
    assert invoice is not None

    assert invoice.reference == "FV/01/2024"
    assert invoice.buyer_id == owner_company.id
    assert invoice.seller_id == client_company.id
    assert invoice.status == FinancialRecordStatus.NEW_COST
    assert invoice.payment_method == PaymentMethod.UNKNOWN
    assert invoice.payment_status == PaymentStatus.UNKNOWN
    assert invoice.primary_document_path == "raw/FV01.pdf"


def test_pdf_ingest_creates_duplicate_on_ocr_collision(invoice_repo,pdf_ingest_service,owner_company,client_company) -> None:
    # -------------------------------------------------
    # GIVEN
    # -------------------------------------------------
    repo = invoice_repo
    service = pdf_ingest_service

    update = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/01/2024",
        record_id=None,
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.UNKNOWN,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNKNOWN,
        status=FinancialRecordStatus.NEW_COST,
        scan_filename="raw/FV01.pdf",
        tags=None,
    )

    # -------------------------------------------------
    # WHEN (first ingest)
    # -------------------------------------------------
    ref_map_1 = service.apply([update])
    ref_1 = ref_map_1["FV/01/2024"]
    invoice_1 = repo.get(ref_1.record_id)

    # -------------------------------------------------
    # WHEN (second ingest – same PDF)
    # -------------------------------------------------
    ref_map_2 = service.apply([update])

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert len(repo.list_all()) == 2

    invoice_numbers = {inv.reference for inv in repo.list_all()}

    assert "FV/01/2024" in invoice_numbers
    assert "FV/01/2024-duplicate" in invoice_numbers

    ref_2 = ref_map_2["FV/01/2024-duplicate"]
    assert ref_2.action == RecordApplyAction.APPLIED

def test_pdf_ingest_requires_invoice_number(invoice_repo, pdf_ingest_service,owner_company,client_company) -> None:
    # -------------------------------------------------
    # GIVEN
    # -------------------------------------------------

    update = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="",  # ❌ brak numeru
        record_id=None,
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.UNKNOWN,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNKNOWN,
        status=FinancialRecordStatus.NEW_COST,
        scan_filename="raw/no_number.pdf",
        tags=None,
    )

    # -------------------------------------------------
    # WHEN / THEN
    # -------------------------------------------------
    with pytest.raises(ValueError, match="invoice_number"):
        pdf_ingest_service.apply([update])