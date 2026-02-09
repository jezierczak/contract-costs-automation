from uuid import uuid4, UUID

import pytest

from contract_costs.model.financial_record import (
    FinancialRecordStatus,
    PaymentMethod,
    PaymentStatus,
)
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import (
    InvoiceCommand,
)
from contract_costs.services.financial_records.assigment.ingest.excel_financial_record_ingest_service import (
    ExcelFinancialRecordIngestService,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    ResolvedFinancialRecordUpdate,
)
from contract_costs.services.financial_records.assigment.ingest.dto.invoice_ref_result import (
    RecordApplyAction,
)


def test_excel_ingest_creates_invoice(invoice_repo,    excel_ingest_service,
                                      owner_company,client_company) -> None:
    # -------------------------------------------------
    # GIVEN
    # -------------------------------------------------
    service = excel_ingest_service


    update = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/EX/01",
        record_id=uuid4(),
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=FinancialRecordStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_01.pdf",
        tags=None,
    )

    # -------------------------------------------------
    # WHEN
    # -------------------------------------------------
    ref_map = service.apply([update])

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert "FV/EX/01" in ref_map

    ref = ref_map["FV/EX/01"]
    assert ref.action == RecordApplyAction.APPLIED
    assert isinstance(ref.record_id, UUID)

    invoice = invoice_repo.get(ref.record_id)
    assert invoice is not None

    assert invoice.reference == "FV/EX/01"
    assert invoice.buyer_id == owner_company.id
    assert invoice.seller_id == client_company.id
    assert invoice.status == FinancialRecordStatus.IN_PROGRESS
    assert invoice.payment_method == PaymentMethod.BANK_TRANSFER
    assert invoice.payment_status == PaymentStatus.UNPAID
    assert invoice.primary_document_path == "draft/FV_EX_01.pdf"


def test_excel_ingest_modifies_existing_invoice(
    invoice_repo,
    excel_ingest_service,
        owner_company,client_company
) -> None:
    # -------------------------------------------------
    # GIVEN — istniejąca faktura
    # -------------------------------------------------
    service = excel_ingest_service

    original = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/EX/02",
        record_id=uuid4(),
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=FinancialRecordStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_02.pdf",
        tags=None,
    )

    ref_map_1 = service.apply([original])
    ref_1 = ref_map_1["FV/EX/02"]
    invoice_id = ref_1.record_id

    # -------------------------------------------------
    # WHEN — Excel zmienia dane
    # -------------------------------------------------
    updated = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/EX/02",  # ten sam numer
        record_id=invoice_id,
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.CASH,  # 🔥 zmiana
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.PAID,  # 🔥 zmiana
        status=FinancialRecordStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_02_v2.pdf",  # 🔥 zmiana
        tags=None,
    )

    ref_map_2 = service.apply([updated])
    ref_2 = ref_map_2["FV/EX/02"]

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert ref_2.record_id == invoice_id
    assert ref_2.action == RecordApplyAction.APPLIED

    invoice = invoice_repo.get(invoice_id)
    assert invoice.payment_method == PaymentMethod.CASH

def test_excel_ingest_deletes_invoice(
    invoice_repo,
    excel_ingest_service,
        owner_company,client_company
) -> None:
    # -------------------------------------------------
    # GIVEN — istniejąca faktura
    # -------------------------------------------------
    service = excel_ingest_service


    create = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/EX/03",
        record_id=None,
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=FinancialRecordStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_03.pdf",
        tags=None,
    )

    ref_map_1 = service.apply([create])
    ref_1 = ref_map_1["FV/EX/03"]
    invoice_id = ref_1.record_id

    # -------------------------------------------------
    # WHEN — Excel DELETE
    # -------------------------------------------------
    delete = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.DELETE,
        reference="FV/EX/03",
        record_id=invoice_id,
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=FinancialRecordStatus.DELETED,  # status z Excela
        scan_filename="draft/FV_EX_03.pdf",
        tags=None,
    )

    ref_map_2 = service.apply([delete])
    ref_2 = ref_map_2["FV/EX/03"]

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert ref_2.record_id == invoice_id
    assert ref_2.action == RecordApplyAction.DELETED

    invoice = invoice_repo.get(invoice_id)
    assert invoice is not None
    assert invoice.status == FinancialRecordStatus.DELETED


def test_excel_ingest_skips_processed_invoice(
    invoice_repo,
    excel_ingest_service,
        owner_company,client_company
) -> None:
    # -------------------------------------------------
    # GIVEN — istniejąca, przetworzona faktura
    # -------------------------------------------------
    service = excel_ingest_service

    create = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/EX/04",
        record_id=None,
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=FinancialRecordStatus.PROCESSED,
        scan_filename="final/FV_EX_04.pdf",
        tags=None,
    )

    ref_map_1 = service.apply([create])
    ref_1 = ref_map_1["FV/EX/04"]
    invoice_id = ref_1.record_id

    invoice_before = invoice_repo.get(invoice_id)

    assert invoice_before.status == FinancialRecordStatus.PROCESSED
    # assert invoice_id == create.invoice_id

    # -------------------------------------------------
    # WHEN — Excel próbuje zmodyfikować PROCESSED
    # -------------------------------------------------
    update = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/EX/04",
        record_id=invoice_id,
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.CASH,  # ❌ próba zmiany
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.PAID,  # ❌ próba zmiany
        status=FinancialRecordStatus.IN_PROGRESS,
        scan_filename="draft/SHOULD_NOT_CHANGE.pdf",
        tags=None,
    )

    ref_map_2 = service.apply([update])
    ref_2 = ref_map_2["FV/EX/04"]

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert ref_2.action == RecordApplyAction.SKIPPED
    assert ref_2.record_id == invoice_id

    invoice_after = invoice_repo.get(invoice_id)

    # brak zmian
    assert invoice_after.payment_method == invoice_before.payment_method
    assert invoice_after.payment_status == invoice_before.payment_status
    assert invoice_after.primary_document_path == invoice_before.primary_document_path


@pytest.mark.skip(reason="legacy behavior: old_invoice_number delete flow")
def test_excel_ingest_renames_invoice_number(
    invoice_repo,
    excel_ingest_service,
        owner_company,client_company
) -> None:
    # -------------------------------------------------
    # GIVEN — istniejąca faktura
    # -------------------------------------------------
    service = excel_ingest_service

    original = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/EX/05",
        record_id=None,
        old_record_reference=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=FinancialRecordStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_05.pdf",
        tags=None,
    )

    ref_map_1 = service.apply([original])
    old_ref = ref_map_1["FV/EX/05"]
    old_invoice_id = old_ref.record_id

    # -------------------------------------------------
    # WHEN — Excel zmienia numer faktury
    # -------------------------------------------------
    renamed = ResolvedFinancialRecordUpdate(
        command=InvoiceCommand.APPLY,
        reference="FV/EX/05A",          # 🔥 nowy numer
        record_id=None,
        old_record_reference="FV/EX/05",       # 🔥 stary numer
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=FinancialRecordStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_05A.pdf",
        tags=None,
    )

    ref_map_2 = service.apply([renamed])
    new_ref = ref_map_2["FV/EX/05A"]
    new_invoice_id = new_ref.record_id

    # -------------------------------------------------
    # THEN — nowa faktura
    # -------------------------------------------------
    assert new_invoice_id != old_invoice_id

    new_invoice = invoice_repo.get(new_invoice_id)
    assert new_invoice is not None
    assert new_invoice.reference == "FV/EX/05A"
    assert new_invoice.status == FinancialRecordStatus.IN_PROGRESS

    # -------------------------------------------------
    # THEN — stara faktura oznaczona jako DELETED
    # -------------------------------------------------
    old_invoice = invoice_repo.get(old_invoice_id)
    assert old_invoice is not None
    assert old_invoice.reference == "FV/EX/05"
    assert old_invoice.status == FinancialRecordStatus.DELETED
