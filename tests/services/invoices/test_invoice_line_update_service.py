from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.amount import Amount, VatRate

from contract_costs.services.invoices.dto.common import InvoiceLineUpdate
from contract_costs.services.invoices.dto.apply import (
    InvoiceRefResult,
    InvoiceApplyAction,
)

@pytest.fixture
def invoice_id():
    return uuid4()


@pytest.fixture
def ref_map(invoice_id):
    return {
        "FV/1": InvoiceRefResult(
            invoice_id=invoice_id,
            action=InvoiceApplyAction.APPLIED,
            invoice_number="FV/1",
            old_invoice_number=None,
        )
    }


@pytest.fixture
def skipped_ref_map(invoice_id):
    return {
        "FV/1": InvoiceRefResult(
            invoice_id=invoice_id,
            action=InvoiceApplyAction.SKIPPED,
            invoice_number="FV/1",
            old_invoice_number=None,
        )
    }


@pytest.fixture
def deleted_ref_map(invoice_id):
    return {
        "FV/1": InvoiceRefResult(
            invoice_id=invoice_id,
            action=InvoiceApplyAction.DELETED,
            invoice_number="FV/1",
            old_invoice_number=None,
        )
    }


# ======================================================================
# HELPERY
# ======================================================================

def make_line_update(**kwargs) -> InvoiceLineUpdate:
    return InvoiceLineUpdate(
        invoice_line_id=kwargs.get("invoice_line_id"),
        invoice_number=kwargs.get("invoice_number", "FV/1"),
        item_name=kwargs.get("item_name", "Item A"),
        description=kwargs.get("description", "Desc A"),
        quantity=Decimal("1"),
        unit=UnitOfMeasure.PIECE,
        amount=Amount(Decimal("100"), VatRate.VAT_23),
        contract_id=kwargs.get("contract_id"),
        cost_node_id=kwargs.get("cost_node_id"),
        cost_type_id=kwargs.get("cost_type_id"),
    )


# ======================================================================
# TESTS
# ======================================================================

def test_create_new_invoice_line(invoice_line_update_service, invoice_line_repo, ref_map, invoice_id):
    update = make_line_update()

    result = invoice_line_update_service.apply([update], ref_map)

    lines = invoice_line_repo.list_lines()
    assert len(lines) == 1
    assert lines[0].invoice_id == invoice_id
    assert result == set()  # niepełna linia → brak fully assigned


def test_update_existing_invoice_line_overwrites_invoice_id(
    invoice_line_update_service, invoice_line_repo, ref_map, invoice_id
):
    old_invoice_id = uuid4()

    existing = InvoiceLine(
        id=uuid4(),
        invoice_id=old_invoice_id,
        item_name="Old",
        description="Old desc",
        quantity=Decimal("1"),
        unit=UnitOfMeasure.PIECE,
        amount=Amount(Decimal("50"), VatRate.VAT_23),
        contract_id=None,
        cost_node_id=None,
        cost_type_id=None,
    )
    invoice_line_repo.add(existing)

    update = make_line_update(
        invoice_line_id=existing.id,
        description="Updated desc",
    )

    invoice_line_update_service.apply([update], ref_map)

    updated = invoice_line_repo.get(existing.id)
    assert updated.description == "Updated desc"
    assert updated.invoice_id == invoice_id  # 🔥 overwrite


def test_delete_lines_not_in_excel(
    invoice_line_update_service, invoice_line_repo, ref_map, invoice_id
):
    l1 = InvoiceLine(
        id=uuid4(),
        invoice_id=invoice_id,
        item_name="A",
        description=None,
        quantity=None,
        unit=UnitOfMeasure.PIECE,
        amount=Amount(Decimal("10"), VatRate.VAT_23),
        contract_id=None,
        cost_node_id=None,
        cost_type_id=None,
    )
    l2 = InvoiceLine(
        id=uuid4(),
        invoice_id=invoice_id,
        item_name="B",
        description=None,
        quantity=None,
        unit=UnitOfMeasure.PIECE,
        amount=Amount(Decimal("20"), VatRate.VAT_23),
        contract_id=None,
        cost_node_id=None,
        cost_type_id=None,
    )

    invoice_line_repo.add(l1)
    invoice_line_repo.add(l2)

    update = make_line_update(invoice_line_id=l1.id)

    invoice_line_update_service.apply([update], ref_map)

    lines = invoice_line_repo.list_lines()
    assert len(lines) == 1
    assert lines[0].id == l1.id


def test_delete_all_lines_when_excel_has_zero_lines(
    invoice_line_update_service, invoice_line_repo, ref_map, invoice_id
):
    invoice_line_repo.add(
        InvoiceLine(
            id=uuid4(),
            invoice_id=invoice_id,
            item_name="X",
            description=None,
            quantity=None,
            unit=UnitOfMeasure.PIECE,
            amount=Amount(Decimal("10"), VatRate.VAT_23),
            contract_id=None,
            cost_node_id=None,
            cost_type_id=None,
        )
    )

    invoice_line_update_service.apply([], ref_map)

    assert invoice_line_repo.list_lines() == []


def test_lines_are_skipped_for_skipped_invoice(
    invoice_line_update_service, invoice_line_repo, skipped_ref_map
):
    update = make_line_update()

    invoice_line_update_service.apply([update], skipped_ref_map)

    assert invoice_line_repo.list_lines() == []


def test_lines_are_skipped_for_deleted_invoice(
    invoice_line_update_service, invoice_line_repo, deleted_ref_map
):
    update = make_line_update()

    invoice_line_update_service.apply([update], deleted_ref_map)

    assert invoice_line_repo.list_lines() == []


def test_line_with_unknown_invoice_reference_is_skipped(
    invoice_line_update_service, invoice_line_repo
):
    update = make_line_update(invoice_number="FV/UNKNOWN")

    invoice_line_update_service.apply([update], ref_map={})

    assert invoice_line_repo.list_lines() == []


def test_fully_assigned_invoice_id_is_returned(
    invoice_line_update_service, ref_map, invoice_id
):
    update = make_line_update(
        contract_id="C1",
        cost_node_id="N1",
        cost_type_id="MATERIAL",  # 👈 zgodnie z conftest
    )

    result = invoice_line_update_service.apply([update], ref_map)

    assert result == {invoice_id}


def test_invoice_not_fully_assigned_when_missing_cost_type(
    invoice_line_update_service, ref_map
):
    update = make_line_update(
        contract_id="C1",
        cost_node_id="N1",
        cost_type_id=None,
    )

    result = invoice_line_update_service.apply([update], ref_map)

    assert result == set()
