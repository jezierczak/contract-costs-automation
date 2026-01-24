from uuid import uuid4, UUID

import pytest

from contract_costs.model.invoice import (
    InvoiceStatus,
    PaymentMethod,
    PaymentStatus,
)
from contract_costs.services.invoices.assigment.apply.commands.invoice_command import (
    InvoiceCommand,
)
from contract_costs.services.invoices.assigment.ingest.excel_invoice_ingest_service import (
    ExcelInvoiceIngestService,
)
from contract_costs.services.invoices.assigment.invoice_sources.dto.common import (
    ResolvedInvoiceUpdate,
)
from contract_costs.services.invoices.assigment.ingest.dto.invoice_ref_result import (
    InvoiceApplyAction,
)


def test_excel_ingest_creates_invoice(invoice_repo,    excel_ingest_service,
                                      owner_company,client_company) -> None:
    # -------------------------------------------------
    # GIVEN
    # -------------------------------------------------
    service = excel_ingest_service


    update = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/EX/01",
        invoice_id=uuid4(),
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.IN_PROGRESS,
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
    assert ref.action == InvoiceApplyAction.APPLIED
    assert isinstance(ref.invoice_id, UUID)

    invoice = invoice_repo.get(ref.invoice_id)
    assert invoice is not None

    assert invoice.invoice_number == "FV/EX/01"
    assert invoice.buyer_id == owner_company.id
    assert invoice.seller_id == client_company.id
    assert invoice.status == InvoiceStatus.IN_PROGRESS
    assert invoice.payment_method == PaymentMethod.BANK_TRANSFER
    assert invoice.payment_status == PaymentStatus.UNPAID
    assert invoice.scan_filename == "draft/FV_EX_01.pdf"


def test_excel_ingest_modifies_existing_invoice(
    invoice_repo,
    excel_ingest_service,
        owner_company,client_company
) -> None:
    # -------------------------------------------------
    # GIVEN — istniejąca faktura
    # -------------------------------------------------
    service = excel_ingest_service

    original = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/EX/02",
        invoice_id=uuid4(),
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_02.pdf",
        tags=None,
    )

    ref_map_1 = service.apply([original])
    ref_1 = ref_map_1["FV/EX/02"]
    invoice_id = ref_1.invoice_id

    # -------------------------------------------------
    # WHEN — Excel zmienia dane
    # -------------------------------------------------
    updated = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/EX/02",  # ten sam numer
        invoice_id=invoice_id,
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.CASH,  # 🔥 zmiana
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.PAID,  # 🔥 zmiana
        status=InvoiceStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_02_v2.pdf",  # 🔥 zmiana
        tags=None,
    )

    ref_map_2 = service.apply([updated])
    ref_2 = ref_map_2["FV/EX/02"]

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert ref_2.invoice_id == invoice_id
    assert ref_2.action == InvoiceApplyAction.APPLIED

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


    create = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/EX/03",
        invoice_id=None,
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_03.pdf",
        tags=None,
    )

    ref_map_1 = service.apply([create])
    ref_1 = ref_map_1["FV/EX/03"]
    invoice_id = ref_1.invoice_id

    # -------------------------------------------------
    # WHEN — Excel DELETE
    # -------------------------------------------------
    delete = ResolvedInvoiceUpdate(
        command=InvoiceCommand.DELETE,
        invoice_number="FV/EX/03",
        invoice_id=invoice_id,
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.DELETED,  # status z Excela
        scan_filename="draft/FV_EX_03.pdf",
        tags=None,
    )

    ref_map_2 = service.apply([delete])
    ref_2 = ref_map_2["FV/EX/03"]

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert ref_2.invoice_id == invoice_id
    assert ref_2.action == InvoiceApplyAction.DELETED

    invoice = invoice_repo.get(invoice_id)
    assert invoice is not None
    assert invoice.status == InvoiceStatus.DELETED


def test_excel_ingest_skips_processed_invoice(
    invoice_repo,
    excel_ingest_service,
        owner_company,client_company
) -> None:
    # -------------------------------------------------
    # GIVEN — istniejąca, przetworzona faktura
    # -------------------------------------------------
    service = excel_ingest_service

    create = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/EX/04",
        invoice_id=None,
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.PROCESSED,
        scan_filename="final/FV_EX_04.pdf",
        tags=None,
    )

    ref_map_1 = service.apply([create])
    ref_1 = ref_map_1["FV/EX/04"]
    invoice_id = ref_1.invoice_id

    invoice_before = invoice_repo.get(invoice_id)

    assert invoice_before.status == InvoiceStatus.PROCESSED
    # assert invoice_id == create.invoice_id

    # -------------------------------------------------
    # WHEN — Excel próbuje zmodyfikować PROCESSED
    # -------------------------------------------------
    update = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/EX/04",
        invoice_id=invoice_id,
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.CASH,  # ❌ próba zmiany
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.PAID,  # ❌ próba zmiany
        status=InvoiceStatus.IN_PROGRESS,
        scan_filename="draft/SHOULD_NOT_CHANGE.pdf",
        tags=None,
    )

    ref_map_2 = service.apply([update])
    ref_2 = ref_map_2["FV/EX/04"]

    # -------------------------------------------------
    # THEN
    # -------------------------------------------------
    assert ref_2.action == InvoiceApplyAction.SKIPPED
    assert ref_2.invoice_id == invoice_id

    invoice_after = invoice_repo.get(invoice_id)

    # brak zmian
    assert invoice_after.payment_method == invoice_before.payment_method
    assert invoice_after.payment_status == invoice_before.payment_status
    assert invoice_after.scan_filename == invoice_before.scan_filename


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

    original = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/EX/05",
        invoice_id=None,
        old_invoice_number=None,
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_05.pdf",
        tags=None,
    )

    ref_map_1 = service.apply([original])
    old_ref = ref_map_1["FV/EX/05"]
    old_invoice_id = old_ref.invoice_id

    # -------------------------------------------------
    # WHEN — Excel zmienia numer faktury
    # -------------------------------------------------
    renamed = ResolvedInvoiceUpdate(
        command=InvoiceCommand.APPLY,
        invoice_number="FV/EX/05A",          # 🔥 nowy numer
        invoice_id=None,
        old_invoice_number="FV/EX/05",       # 🔥 stary numer
        invoice_date=None,
        selling_date=None,
        buyer=owner_company,
        seller=client_company,
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.IN_PROGRESS,
        scan_filename="draft/FV_EX_05A.pdf",
        tags=None,
    )

    ref_map_2 = service.apply([renamed])
    new_ref = ref_map_2["FV/EX/05A"]
    new_invoice_id = new_ref.invoice_id

    # -------------------------------------------------
    # THEN — nowa faktura
    # -------------------------------------------------
    assert new_invoice_id != old_invoice_id

    new_invoice = invoice_repo.get(new_invoice_id)
    assert new_invoice is not None
    assert new_invoice.invoice_number == "FV/EX/05A"
    assert new_invoice.status == InvoiceStatus.IN_PROGRESS

    # -------------------------------------------------
    # THEN — stara faktura oznaczona jako DELETED
    # -------------------------------------------------
    old_invoice = invoice_repo.get(old_invoice_id)
    assert old_invoice is not None
    assert old_invoice.invoice_number == "FV/EX/05"
    assert old_invoice.status == InvoiceStatus.DELETED
