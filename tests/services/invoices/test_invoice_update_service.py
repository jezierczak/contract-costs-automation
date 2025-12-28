from datetime import date, datetime
from uuid import uuid4

import pytest

from contract_costs.model.invoice import InvoiceStatus, Invoice, PaymentMethod, PaymentStatus
from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository
from contract_costs.services.invoices.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.dto.apply import InvoiceApplyAction
from contract_costs.services.invoices.dto.common import ResolvedInvoiceUpdate
from contract_costs.services.invoices.invoice_update_service import InvoiceUpdateService

@pytest.fixture
def invoice_repo():
    return InMemoryInvoiceRepository()

@pytest.fixture
def service(invoice_repo):
    return InvoiceUpdateService(invoice_repo)



def resolved_update(**kwargs):
    return ResolvedInvoiceUpdate(
        invoice_number=kwargs.get("invoice_number", "FV/1"),
        old_invoice_number=kwargs.get("old_invoice_number"),
        invoice_date=date(2024, 1, 1),
        selling_date=date(2024, 1, 1),
        buyer_id=kwargs.get("buyer_id", uuid4()),
        seller_id=kwargs.get("seller_id", uuid4()),
        payment_method=PaymentMethod.BANK_TRANSFER,
        payment_status=PaymentStatus.UNPAID,
        due_date=date(2024, 1, 31),
        status=kwargs.get("status", InvoiceStatus.IN_PROGRESS),
        command=kwargs.get("command", InvoiceCommand.APPLY),
    )


def test_create_new_invoice(service, invoice_repo):
    update = resolved_update()

    result = service.apply([update])

    assert result["FV/1"].action == InvoiceApplyAction.APPLIED
    invoices = invoice_repo.list_invoices()
    assert len(invoices) == 1
    assert invoices[0].status == InvoiceStatus.IN_PROGRESS



def test_update_existing_invoice(service, invoice_repo):
    existing = Invoice(
        id=uuid4(),
        invoice_number="FV/1",
        invoice_date=date(2024, 1, 1),
        selling_date=date(2024, 1, 1),
        buyer_id=uuid4(),
        seller_id=uuid4(),
        payment_method=PaymentMethod.CASH,
        due_date=date(2024, 1, 31),
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.IN_PROGRESS,
        timestamp=datetime.now(),
    )
    invoice_repo.add(existing)

    update = resolved_update(
        invoice_number="FV/1",
        seller_id=existing.seller_id,
        status=InvoiceStatus.PROCESSED,
    )

    result = service.apply([update])

    updated = invoice_repo.get(existing.id)
    assert updated.status == InvoiceStatus.PROCESSED
    assert result["FV/1"].action.name == "APPLIED"


def test_skip_processed_invoice(service, invoice_repo):
    inv = Invoice(
        id=uuid4(),
        invoice_number="FV/1",
        invoice_date=date(2024, 1, 1),
        selling_date=date(2024, 1, 1),
        buyer_id=uuid4(),
        seller_id=uuid4(),
        payment_method=PaymentMethod.CASH,
        due_date=date(2024, 1, 31),
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.PROCESSED,
        timestamp=datetime.now(),
    )
    invoice_repo.add(inv)

    update = resolved_update(
        invoice_number="FV/1",
        seller_id=inv.seller_id,
    )

    result = service.apply([update])

    assert result["FV/1"].action == InvoiceApplyAction.SKIPPED

def test_delete_non_existing_invoice_is_skipped(service):
    update = resolved_update(
        invoice_number="FV/404",
        command=InvoiceCommand.DELETE,
    )

    result = service.apply([update])

    assert result["FV/404"].action == InvoiceApplyAction.SKIPPED

def test_invoice_number_change_creates_new_and_deletes_old(service, invoice_repo):
    old = Invoice(
        id=uuid4(),
        invoice_number="FV/OLD",
        invoice_date=date(2024, 1, 1),
        selling_date=date(2024, 1, 1),
        buyer_id=uuid4(),
        seller_id=uuid4(),
        payment_method=PaymentMethod.CASH,
        due_date=date(2024, 1, 31),
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.IN_PROGRESS,
        timestamp=datetime.now(),
    )
    invoice_repo.add(old)

    update = resolved_update(
        invoice_number="FV/NEW",
        old_invoice_number="FV/OLD",
        seller_id=old.seller_id,
    )

    result = service.apply([update])

    # nowa faktura utworzona
    assert result["FV/NEW"].action == InvoiceApplyAction.APPLIED
    assert result["FV/NEW"].invoice_id is not None

    invoices = invoice_repo.list_invoices()
    assert len(invoices) == 2

    # stara logicznie usunięta
    old_updated = invoice_repo.get(old.id)
    assert old_updated.status == InvoiceStatus.DELETED


def test_missing_invoice_number_raises():
    service = InvoiceUpdateService(InMemoryInvoiceRepository())

    update = resolved_update(invoice_number="   ")

    with pytest.raises(ValueError):
        service.apply([update])

def test_duplicate_invoice_number_in_batch():
    service = InvoiceUpdateService(InMemoryInvoiceRepository())

    u1 = resolved_update(invoice_number="FV/1")
    u2 = resolved_update(invoice_number="FV/1")

    with pytest.raises(ValueError):
        service.apply([u1, u2])
