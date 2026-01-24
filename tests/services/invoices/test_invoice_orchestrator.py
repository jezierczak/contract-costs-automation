from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.invoice import PaymentMethod, PaymentStatus, InvoiceStatus, Invoice
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.invoices.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.assigment.invoice_sources.dto.common import InvoiceIngestBatch, \
    ResolvedInvoiceUpdate, InvoiceLineUpdate


def test_ingest_from_pdf_creates_invoice_and_lines_without_finalization(
    orchestrator,
    invoice_repo,
    invoice_line_repo,
        owner_company,client_company
):
    batch = InvoiceIngestBatch(
        invoices=[
            ResolvedInvoiceUpdate(
                command=InvoiceCommand.APPLY,
                invoice_number="FV/PDF/1",
                invoice_id=None,
                old_invoice_number=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=InvoiceStatus.IN_PROGRESS,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[
            InvoiceLineUpdate(
                invoice_line_id=None,
                invoice_number="FV/PDF/1",
                item_name="Material A",
                description=None,
                quantity=Decimal("1"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(Decimal("100"), VatRate.VAT_23),
                contract_id=None,
                contract_node_id=None,
                value_type_code=None,
            )
        ],
    )

    orchestrator.ingest_from_pdf(batch)

    invoices = invoice_repo.list_invoices()
    assert len(invoices) == 1
    assert invoices[0].status == InvoiceStatus.IN_PROGRESS

    lines = invoice_line_repo.list_lines()
    assert len(lines) == 1
def test_ingest_from_excel_finalizes_invoice_when_lines_fully_assigned(
    orchestrator,
    invoice_repo,
    invoice_line_repo,
        owner_company,client_company
):
    batch = InvoiceIngestBatch(
        invoices=[
            ResolvedInvoiceUpdate(
                command=InvoiceCommand.APPLY,
                invoice_number="FV/XLS/1",
                invoice_id=None,
                old_invoice_number=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=InvoiceStatus.IN_PROGRESS,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[
            InvoiceLineUpdate(
                invoice_line_id=None,
                invoice_number="FV/XLS/1",
                item_name="Material A",
                description=None,
                quantity=Decimal("1"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(Decimal("100"), VatRate.VAT_23),
                contract_id="C1",
                contract_node_id="N1",
                value_type_code="MATERIAL",
            )
        ],
    )

    orchestrator.ingest_from_excel(batch)

    seller_id = batch.invoices[0].seller.id
    invoice = invoice_repo.get_unique_invoice("FV/XLS/1", seller_id)

    assert invoice is not None
    assert invoice.status == InvoiceStatus.PROCESSED


def test_ingest_from_excel_does_not_finalize_when_lines_incomplete(
    orchestrator,
    invoice_repo,
        owner_company,client_company
):
    batch = InvoiceIngestBatch(
        invoices=[
            ResolvedInvoiceUpdate(
                command=InvoiceCommand.APPLY,
                invoice_number="FV/XLS/2",
                invoice_id=None,
                old_invoice_number=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=InvoiceStatus.IN_PROGRESS,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[
            InvoiceLineUpdate(
                invoice_line_id=None,
                invoice_number="FV/XLS/2",
                item_name="Material A",
                description=None,
                quantity=Decimal("1"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(Decimal("100"), VatRate.VAT_23),
                contract_id="C1",
                contract_node_id=None,   # ❌ brak
                value_type_code="MATERIAL",
            )
        ],
    )

    orchestrator.ingest_from_excel(batch)

    seller_id = batch.invoices[0].seller.id
    invoice = invoice_repo.get_unique_invoice("FV/XLS/2", seller_id)
    assert invoice is not None
    assert invoice.status == InvoiceStatus.IN_PROGRESS


def test_ingest_from_excel_delete_does_not_finalize(
    orchestrator,
    invoice_repo,
        owner_company,client_company
):
    batch = InvoiceIngestBatch(
        invoices=[
            ResolvedInvoiceUpdate(
                command=InvoiceCommand.DELETE,
                invoice_number="FV/XLS/DEL",
                invoice_id=None,
                old_invoice_number=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=InvoiceStatus.DELETED,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[],
    )

    orchestrator.ingest_from_excel(batch)

    seller_id = batch.invoices[0].seller
    invoice = invoice_repo.get_unique_invoice("FV/XLS/DEL", seller_id)
    assert invoice is None

def test_ingest_from_excel_delete_existing_invoice(
    orchestrator,
    invoice_repo,
        owner_company,
        client_company,
):
    inv_id = uuid4()
    # GIVEN: istniejąca faktura
    invoice_repo.add(
        Invoice(
            id=inv_id,
            invoice_number="FV/XLS/DEL",
            invoice_date=date(2024, 1, 1),
            selling_date=date(2024, 1, 1),
            buyer_id=owner_company.id,
            seller_id=client_company.id,
            payment_method=PaymentMethod.BANK_TRANSFER,
            due_date=date(2024, 1, 31),
            paid_date=None,
            payment_status=PaymentStatus.UNPAID,
            status=InvoiceStatus.IN_PROGRESS,
            timestamp=datetime.now(),
            scan_filename=None,
            tags=set()
        )
    )

    batch = InvoiceIngestBatch(
        invoices=[
            ResolvedInvoiceUpdate(
                command=InvoiceCommand.DELETE,
                invoice_number="FV/XLS/DEL",
                invoice_id=inv_id,
                old_invoice_number=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,  # 👈 TEN SAM SELLER
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=InvoiceStatus.DELETED,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[],
    )

    orchestrator.ingest_from_excel(batch)

    invoices = invoice_repo.get_by_invoice_number("FV/XLS/DEL")
    assert invoices is not None

    #only one invoice so first is always deleted
    for invoice in invoices:
        assert invoice.status == InvoiceStatus.DELETED
        assert invoice.invoice_number == "FV/XLS/DEL"

def test_ingest_from_excel_changes_invoice_number_and_deletes_old(
    orchestrator,
    invoice_repo,
    invoice_line_repo,
        owner_company,
        client_company,
):
    # -------------------------------------------------
    # GIVEN: istniejąca faktura z PDF (IN_PROGRESS)
    # -------------------------------------------------

    old_invoice = Invoice(
        id=uuid4(),
        invoice_number="FV/OLD",
        invoice_date=date(2024, 1, 1),
        selling_date=date(2024, 1, 1),
        buyer_id=owner_company.id,
        seller_id=client_company.id,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=date(2024, 1, 31),
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.IN_PROGRESS,
        timestamp=datetime.now(),
        scan_filename=None,
        tags=set()
    )
    invoice_repo.add(old_invoice)

    old_line = InvoiceLine(
        id=uuid4(),
        invoice_id=old_invoice.id,
        item_name="Material A",
        description=None,
        quantity=Decimal("1"),
        unit=UnitOfMeasure.PIECE,
        amount=Amount(Decimal("100"), VatRate.VAT_23),
        contract_id=None,
        contract_node_id=None,
        value_type_id=None,
    )
    invoice_line_repo.add(old_line)

    # -------------------------------------------------
    # WHEN: Excel zmienia numer faktury
    # -------------------------------------------------
    batch = InvoiceIngestBatch(
        invoices=[
            ResolvedInvoiceUpdate(
                command=InvoiceCommand.APPLY,
                invoice_number="FV/NEW",
                invoice_id=old_invoice.id,
                old_invoice_number="FV/OLD",
                invoice_date=old_invoice.invoice_date,
                selling_date=old_invoice.selling_date,
                buyer=owner_company,
                seller=client_company,
                payment_method=old_invoice.payment_method,
                due_date=old_invoice.due_date,
                paid_date=None,
                payment_status=old_invoice.payment_status,
                status=InvoiceStatus.IN_PROGRESS,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[
            InvoiceLineUpdate(
                invoice_line_id=old_line.id,   # 👈 TA SAMA LINIA
                invoice_number="FV/NEW",       # 👈 NOWA FAKTURA
                item_name="Material A",
                description="Updated",
                quantity=Decimal("2"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(Decimal("200"), VatRate.VAT_23),
                contract_id=None,
                contract_node_id=None,
                value_type_code=None,
            )
        ],
    )

    orchestrator.ingest_from_excel(batch)

    # -------------------------------------------------
    # THEN: nie ma starej faktury - to ta sama
    # -------------------------------------------------
    updated = invoice_repo.get(old_invoice.id)

    assert updated.id == old_invoice.id
    assert updated.invoice_number == "FV/NEW"
    assert updated.status == InvoiceStatus.IN_PROGRESS

    # -------------------------------------------------
    # THEN: nowa faktura to ta sama ! ale szukamy tu tyko po danych nie po id
    # -------------------------------------------------
    new_invoice = invoice_repo.get_unique_invoice("FV/NEW", client_company.id)
    assert new_invoice is not None
    assert new_invoice.status == InvoiceStatus.IN_PROGRESS

    #stara i nowa to to samo:

    assert updated.id == new_invoice.id

    # -------------------------------------------------
    # THEN: linia przepięta na nową fakturę
    # -------------------------------------------------
    updated_line = invoice_line_repo.get(old_line.id)
    assert updated_line.invoice_id == new_invoice.id
    assert updated_line.description == "Updated"
    assert updated_line.quantity == Decimal("2")



