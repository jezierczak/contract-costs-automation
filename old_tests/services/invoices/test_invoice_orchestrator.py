from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.financial_record import PaymentMethod, PaymentStatus, FinancialRecordStatus, FinancialRecord
from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import RecordIngestBatch, \
    ResolvedFinancialRecordUpdate, FinancialRecordLineUpdate


def test_ingest_from_pdf_creates_invoice_and_lines_without_finalization(
    orchestrator,
    invoice_repo,
    invoice_line_repo,
        owner_company,client_company
):
    batch = RecordIngestBatch(
        financial_records=[
            ResolvedFinancialRecordUpdate(
                command=InvoiceCommand.APPLY,
                reference="FV/PDF/1",
                record_id=None,
                old_record_reference=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=FinancialRecordStatus.IN_PROGRESS,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[
            FinancialRecordLineUpdate(
                record_line_id=None,
                record_reference="FV/PDF/1",
                item_name="Material A",
                description=None,
                quantity=Decimal("1"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(Decimal("100"), VatRate.VAT_23),
                contract_code=None,
                contract_node_code=None,
                value_type_code=None,
            )
        ],
    )

    orchestrator.ingest_from_document(batch)

    invoices = invoice_repo.list_all()
    assert len(invoices) == 1
    assert invoices[0].status == FinancialRecordStatus.IN_PROGRESS

    lines = invoice_line_repo.list_lines()
    assert len(lines) == 1
def test_ingest_from_excel_finalizes_invoice_when_lines_fully_assigned(
    orchestrator,
    invoice_repo,
    invoice_line_repo,
        owner_company,client_company
):
    batch = RecordIngestBatch(
        financial_records=[
            ResolvedFinancialRecordUpdate(
                command=InvoiceCommand.APPLY,
                reference="FV/XLS/1",
                record_id=None,
                old_record_reference=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=FinancialRecordStatus.IN_PROGRESS,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[
            FinancialRecordLineUpdate(
                record_line_id=None,
                record_reference="FV/XLS/1",
                item_name="Material A",
                description=None,
                quantity=Decimal("1"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(Decimal("100"), VatRate.VAT_23),
                contract_code="C1",
                contract_node_code="N1",
                value_type_code="MATERIAL",
            )
        ],
    )

    orchestrator.ingest_from_excel(batch)

    seller_id = batch.financial_records[0].seller.id
    invoice = invoice_repo.get_unique_record("FV/XLS/1", seller_id)

    assert invoice is not None
    assert invoice.status == FinancialRecordStatus.PROCESSED


def test_ingest_from_excel_does_not_finalize_when_lines_incomplete(
    orchestrator,
    invoice_repo,
        owner_company,client_company
):
    batch = RecordIngestBatch(
        financial_records=[
            ResolvedFinancialRecordUpdate(
                command=InvoiceCommand.APPLY,
                reference="FV/XLS/2",
                record_id=None,
                old_record_reference=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=FinancialRecordStatus.IN_PROGRESS,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[
            FinancialRecordLineUpdate(
                record_line_id=None,
                record_reference="FV/XLS/2",
                item_name="Material A",
                description=None,
                quantity=Decimal("1"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(Decimal("100"), VatRate.VAT_23),
                contract_code="C1",
                contract_node_code=None,   # ❌ brak
                value_type_code="MATERIAL",
            )
        ],
    )

    orchestrator.ingest_from_excel(batch)

    seller_id = batch.financial_records[0].seller.id
    invoice = invoice_repo.get_unique_record("FV/XLS/2", seller_id)
    assert invoice is not None
    assert invoice.status == FinancialRecordStatus.IN_PROGRESS


def test_ingest_from_excel_delete_does_not_finalize(
    orchestrator,
    invoice_repo,
        owner_company,client_company
):
    batch = RecordIngestBatch(
        financial_records=[
            ResolvedFinancialRecordUpdate(
                command=InvoiceCommand.DELETE,
                reference="FV/XLS/DEL",
                record_id=None,
                old_record_reference=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=FinancialRecordStatus.DELETED,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[],
    )

    orchestrator.ingest_from_excel(batch)

    seller_id = batch.financial_records[0].seller
    invoice = invoice_repo.get_unique_record("FV/XLS/DEL", seller_id)
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
        FinancialRecord(
            id=inv_id,
            reference="FV/XLS/DEL",
            invoice_date=date(2024, 1, 1),
            selling_date=date(2024, 1, 1),
            buyer_id=owner_company.id,
            seller_id=client_company.id,
            payment_method=PaymentMethod.BANK_TRANSFER,
            due_date=date(2024, 1, 31),
            paid_date=None,
            payment_status=PaymentStatus.UNPAID,
            status=FinancialRecordStatus.IN_PROGRESS,
            timestamp=datetime.now(),
            scan_filename=None,
            tags=set()
        )
    )

    batch = RecordIngestBatch(
        financial_records=[
            ResolvedFinancialRecordUpdate(
                command=InvoiceCommand.DELETE,
                reference="FV/XLS/DEL",
                record_id=inv_id,
                old_record_reference=None,
                invoice_date=date(2024, 1, 1),
                selling_date=date(2024, 1, 1),
                buyer=owner_company,
                seller=client_company,  # 👈 TEN SAM SELLER
                payment_method=PaymentMethod.BANK_TRANSFER,
                due_date=date(2024, 1, 31),
                paid_date=None,
                payment_status=PaymentStatus.UNPAID,
                status=FinancialRecordStatus.DELETED,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[],
    )

    orchestrator.ingest_from_excel(batch)

    invoices = invoice_repo.get_by_reference("FV/XLS/DEL")
    assert invoices is not None

    #only one invoice so first is always deleted
    for invoice in invoices:
        assert invoice.status == FinancialRecordStatus.DELETED
        assert invoice.reference == "FV/XLS/DEL"

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

    old_invoice = FinancialRecord(
        id=uuid4(),
        reference="FV/OLD",
        invoice_date=date(2024, 1, 1),
        selling_date=date(2024, 1, 1),
        buyer_id=owner_company.id,
        seller_id=client_company.id,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=date(2024, 1, 31),
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=FinancialRecordStatus.IN_PROGRESS,
        timestamp=datetime.now(),
        scan_filename=None,
        tags=set()
    )
    invoice_repo.add(old_invoice)

    old_line = FinancialRecordLine(
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
    batch = RecordIngestBatch(
        financial_records=[
            ResolvedFinancialRecordUpdate(
                command=InvoiceCommand.APPLY,
                reference="FV/NEW",
                record_id=old_invoice.id,
                old_record_reference="FV/OLD",
                invoice_date=old_invoice.invoice_date,
                selling_date=old_invoice.selling_date,
                buyer=owner_company,
                seller=client_company,
                payment_method=old_invoice.payment_method,
                due_date=old_invoice.due_date,
                paid_date=None,
                payment_status=old_invoice.payment_status,
                status=FinancialRecordStatus.IN_PROGRESS,
                scan_filename=None,
                tags=None
            )
        ],
        lines=[
            FinancialRecordLineUpdate(
                record_line_id=old_line.id,   # 👈 TA SAMA LINIA
                record_reference="FV/NEW",       # 👈 NOWA FAKTURA
                item_name="Material A",
                description="Updated",
                quantity=Decimal("2"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(Decimal("200"), VatRate.VAT_23),
                contract_code=None,
                contract_node_code=None,
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
    assert updated.reference == "FV/NEW"
    assert updated.status == FinancialRecordStatus.IN_PROGRESS

    # -------------------------------------------------
    # THEN: nowa faktura to ta sama ! ale szukamy tu tyko po danych nie po id
    # -------------------------------------------------
    new_invoice = invoice_repo.get_unique_record("FV/NEW", client_company.id)
    assert new_invoice is not None
    assert new_invoice.status == FinancialRecordStatus.IN_PROGRESS

    #stara i nowa to to samo:

    assert updated.id == new_invoice.id

    # -------------------------------------------------
    # THEN: linia przepięta na nową fakturę
    # -------------------------------------------------
    updated_line = invoice_line_repo.get(old_line.id)
    assert updated_line.record_id == new_invoice.id
    assert updated_line.description == "Updated"
    assert updated_line.quantity == Decimal("2")



