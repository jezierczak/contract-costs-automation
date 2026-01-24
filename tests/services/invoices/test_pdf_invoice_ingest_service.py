import pytest
from uuid import UUID, uuid4

from contract_costs.model.invoice import InvoiceStatus, PaymentMethod, PaymentStatus
from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository
from contract_costs.services.invoices.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.assigment.ingest.pdf_invoice_ingest_service import (
    PdfInvoiceIngestService,
)
from contract_costs.services.invoices.assigment.invoice_sources.dto.common import (
    ResolvedInvoiceUpdate,
)
from contract_costs.services.invoices.assigment.ingest.dto.invoice_ref_result import (
    InvoiceApplyAction,
)


def test_pdf_ingest_creates_invoice(invoice_repo,pdf_ingest_service,owner_company,client_company) -> None:
    # -------------------------------------------------
    # GIVEN
    # -------------------------------------------------
    repo = invoice_repo
    service = pdf_ingest_service

    update = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/01/2024",
        invoice_id=None,
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.UNKNOWN,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNKNOWN,
        status=InvoiceStatus.NEW_COST,
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
    assert ref.action == InvoiceApplyAction.APPLIED
    assert isinstance(ref.invoice_id, UUID)

    invoice = repo.get(ref.invoice_id)
    assert invoice is not None

    assert invoice.invoice_number == "FV/01/2024"
    assert invoice.buyer_id == owner_company.id
    assert invoice.seller_id == client_company.id
    assert invoice.status == InvoiceStatus.NEW_COST
    assert invoice.payment_method == PaymentMethod.UNKNOWN
    assert invoice.payment_status == PaymentStatus.UNKNOWN
    assert invoice.scan_filename == "raw/FV01.pdf"


def test_pdf_ingest_creates_duplicate_on_ocr_collision(invoice_repo,pdf_ingest_service,owner_company,client_company) -> None:
    # -------------------------------------------------
    # GIVEN
    # -------------------------------------------------
    repo = invoice_repo
    service = pdf_ingest_service

    update = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/01/2024",
        invoice_id=None,
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.UNKNOWN,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNKNOWN,
        status=InvoiceStatus.NEW_COST,
        scan_filename="raw/FV01.pdf",
        tags=None,
    )

    # -------------------------------------------------
    # WHEN (first ingest)
    # -------------------------------------------------
    ref_map_1 = service.apply([update])
    ref_1 = ref_map_1["FV/01/2024"]
    invoice_1 = repo.get(ref_1.invoice_id)

    # -------------------------------------------------
    # WHEN (second ingest – same PDF)
    # -------------------------------------------------
    ref_map_2 = service.apply([update])

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert len(repo.list_invoices()) == 2

    invoice_numbers = {inv.invoice_number for inv in repo.list_invoices()}

    assert "FV/01/2024" in invoice_numbers
    assert "FV/01/2024-duplicate" in invoice_numbers

    ref_2 = ref_map_2["FV/01/2024-duplicate"]
    assert ref_2.action == InvoiceApplyAction.APPLIED

def test_pdf_ingest_requires_invoice_number(invoice_repo, pdf_ingest_service,owner_company,client_company) -> None:
    # -------------------------------------------------
    # GIVEN
    # -------------------------------------------------

    update = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="",  # ❌ brak numeru
        invoice_id=None,
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.UNKNOWN,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNKNOWN,
        status=InvoiceStatus.NEW_COST,
        scan_filename="raw/no_number.pdf",
        tags=None,
    )

    # -------------------------------------------------
    # WHEN / THEN
    # -------------------------------------------------
    with pytest.raises(ValueError, match="invoice_number"):
        pdf_ingest_service.apply([update])