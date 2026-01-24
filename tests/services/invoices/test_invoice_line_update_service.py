from decimal import Decimal
from uuid import uuid4

import pytest

from contract_costs.model.company import CompanyType
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.invoices.assigment.ingest.completion_validator.invoice_completion_reason import \
    InvoiceCompletionReason
from contract_costs.services.invoices.assigment.ingest.completion_validator.invoice_completion_validator import \
    InvoiceCompletionValidator
from contract_costs.services.invoices.assigment.ingest.dto.invoice_assignment_facts import InvoiceAssignmentFacts
from contract_costs.services.invoices.assigment.ingest.dto.invoice_ref_result import InvoiceRefResult, \
    InvoiceApplyAction

from contract_costs.services.invoices.assigment.invoice_sources.dto.common import InvoiceLineUpdate


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
            buyer_role=CompanyType.OWN,
            seller_role=CompanyType.SELLER

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
            buyer_role=CompanyType.OWN,
            seller_role=CompanyType.SELLER
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
            buyer_role=CompanyType.OWN,
            seller_role=CompanyType.SELLER
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
        contract_node_id=kwargs.get("cost_node_id"),
        value_type_code=kwargs.get("cost_type_id"),
    )

def make_line(
    *,
    contract=True,
    node=True,
    value_type_id=None,
) -> InvoiceLine:
    return InvoiceLine(
        id=uuid4(),
        invoice_id=uuid4(),
        item_name="Item",
        description=None,
        quantity=Decimal("1"),
        unit=UnitOfMeasure.PIECE,
        amount=Amount(Decimal("100"), VatRate.VAT_23),
        contract_id=uuid4() if contract else None,
        contract_node_id=uuid4() if node else None,
        value_type_id=value_type_id,
    )

# ======================================================================
# TESTS
# ======================================================================

# def test_create_new_invoice_line(invoice_line_update_service, invoice_line_repo, ref_map, invoice_id):
#     update = make_line_update()
#
#     result = invoice_line_update_service.apply([update], ref_map)
#
#     lines = invoice_line_repo.list_lines()
#     assert len(lines) == 1
#     assert lines[0].invoice_id == invoice_id
#     assert InvoiceCompletionReason.OK not in result  # niepełna linia → brak fully assigned
#

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
        contract_node_id=None,
        value_type_id=None,
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
        contract_node_id=None,
        value_type_id=None,
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
        contract_node_id=None,
        value_type_id=None,
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
            contract_node_id=None,
            value_type_id=None,
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

def test_invoice_not_complete_without_invoice_direction():
    line = make_line(value_type_id=uuid4())

    facts = InvoiceAssignmentFacts(
        invoice_id=uuid4(),
        invoice_lines=[line],
        buyer_role=CompanyType.CLIENT,
        seller_role=CompanyType.CLIENT,
        value_type_directions={
            line.value_type_id: ValueDirection.COST
        }
    )

    assert InvoiceCompletionValidator().validate(facts) is False
    reasons = InvoiceCompletionValidator().status(facts)

    assert InvoiceCompletionReason.NO_INVOICE_DIRECTION in reasons


def test_invoice_not_complete_when_line_missing_assignments():
    line = make_line(contract=False)

    facts = InvoiceAssignmentFacts(
        invoice_id=uuid4(),
        invoice_lines=[line],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.CLIENT,
        value_type_directions={}
    )

    assert InvoiceCompletionValidator().validate(facts) is False
    reasons = InvoiceCompletionValidator().status(facts)

    assert InvoiceCompletionReason.INCOMPLETE_LINES in reasons

def test_invoice_not_complete_without_line_directions():
    line = make_line(value_type_id=None)

    facts = InvoiceAssignmentFacts(
        invoice_id=uuid4(),
        invoice_lines=[line],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.CLIENT,
        value_type_directions={}
    )

    assert InvoiceCompletionValidator().validate(facts) is False
    reasons = InvoiceCompletionValidator().status(facts)

    assert InvoiceCompletionReason.NO_LINE_DIRECTIONS in reasons

def test_invoice_not_complete_with_mixed_line_directions():
    vt1 = uuid4()
    vt2 = uuid4()

    line1 = make_line(value_type_id=vt1)
    line2 = make_line(value_type_id=vt2)

    facts = InvoiceAssignmentFacts(
        invoice_id=uuid4(),
        invoice_lines=[line1, line2],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.CLIENT,
        value_type_directions={
            vt1: ValueDirection.COST,
            vt2: ValueDirection.REVENUE,
        }
    )

    assert InvoiceCompletionValidator().validate(facts) is False
    reasons = InvoiceCompletionValidator().status(facts)

    assert InvoiceCompletionReason.MIXED_LINE_DIRECTIONS in reasons

def test_invoice_not_complete_when_direction_mismatch():
    vt = uuid4()
    line = make_line(value_type_id=vt)

    facts = InvoiceAssignmentFacts(
        invoice_id=uuid4(),
        invoice_lines=[line],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.CLIENT,  # COST
        value_type_directions={
            vt: ValueDirection.REVENUE
        }
    )

    assert InvoiceCompletionValidator().validate(facts) is False
    reasons = InvoiceCompletionValidator().status(facts)

    assert InvoiceCompletionReason.DIRECTION_MISMATCH in reasons

def test_invoice_complete_when_all_conditions_met():
    vt = uuid4()
    line = make_line(value_type_id=vt)

    facts = InvoiceAssignmentFacts(
        invoice_id=uuid4(),
        invoice_lines=[line],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.CLIENT,
        value_type_directions={
            vt: ValueDirection.COST
        }
    )

    assert InvoiceCompletionValidator().validate(facts) is True
    assert InvoiceCompletionValidator().status(facts) == [InvoiceCompletionReason.OK]


def test_internal_invoice_is_valid():
    vt = uuid4()
    line = make_line(value_type_id=vt)

    facts = InvoiceAssignmentFacts(
        invoice_id=uuid4(),
        invoice_lines=[line],
        buyer_role=CompanyType.OWN,
        seller_role=CompanyType.OWN,
        value_type_directions={
            vt: ValueDirection.INTERNAL
        }
    )

    assert InvoiceCompletionValidator().validate(facts) is True
