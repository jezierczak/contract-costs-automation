from datetime import date
from decimal import Decimal

from contract_costs.services.financial_records.queries.dto.financial_record_edit_view import (
    FinancialRecordEditView,
    InvoiceLineEditView,
    PaymentEditView,
)
from contract_costs.services.financial_records.queries.record_edit_workspace_query_service import (
    RecordEditWorkspaceQueryService,
)

TODAY = date(2026, 9, 26)


def _source() -> FinancialRecordEditView:
    line = InvoiceLineEditView(
        record_line_id="line-1",
        item_name="Abonament",
        description="opis",
        quantity=Decimal("1"),
        unit="szt",
        amount_value=Decimal("123.00"),
        vat_rate="0.23",
        amount_type="gross",
        tax_treatment="tax_deductible",
        contract_id="c-1",
        contract_node_id="n-1",
        value_type_id="vt-1",
        agreement_id=None,
        agreement_node_id=None,
        contract_nodes=[],
        agreement_nodes=[],
    )
    return FinancialRecordEditView(
        id="rec-1",
        reference="FV/1/2026",
        invoice_date=date(2026, 8, 1),
        selling_date=date(2026, 7, 31),
        payment_method="transfer",
        payment_status="partially_paid",
        due_date=date(2026, 8, 15),
        paid_date=None,
        payments=[PaymentEditView(id="p-1", amount=Decimal("50"), paid_date=date(2026, 8, 5))],
        paid_amount=Decimal("50"),
        total_amount=Decimal("123.00"),
        is_overpaid=False,
        buyer_name="Nasza",
        buyer_tax_number="1111111111",
        seller_name="Dostawca",
        seller_tax_number="2222222222",
        tags="stałe",
        lines=[line],
        documents=["doc"],
        source_confidence=90,
        source_breakdown={"x": 1},
    )


def _copy():
    service = RecordEditWorkspaceQueryService(
        contract_query_service=None,
        contract_tree_query_service=None,
        value_type_query_service=None,
        today=lambda: TODAY,
    )
    return service._as_copy(_source())


def test_copy_keeps_parties_payment_method_and_lines_one_to_one():
    copy = _copy()

    assert (copy.buyer_tax_number, copy.seller_tax_number) == ("1111111111", "2222222222")
    assert copy.payment_method == "transfer"
    assert copy.tags == "stałe"

    line = copy.lines[0]
    assert line.amount_value == Decimal("123.00")
    assert (line.amount_type, line.vat_rate, line.tax_treatment) == ("gross", "0.23", "tax_deductible")
    assert (line.contract_id, line.contract_node_id, line.value_type_id) == ("c-1", "n-1", "vt-1")


def test_copy_is_a_new_record_without_number_documents_and_payments():
    copy = _copy()

    assert copy.id == ""
    assert copy.reference == ""
    assert copy.documents == []
    assert copy.payments == []
    assert copy.source_confidence is None
    # pusty record_line_id → zapis tworzy nowe linie, oryginał zostaje nietknięty
    assert copy.lines[0].record_line_id == ""


def test_copy_uses_today_and_keeps_payment_term():
    copy = _copy()

    assert copy.invoice_date == TODAY
    assert copy.selling_date == TODAY
    assert copy.due_date == date(2026, 10, 10)  # 14 dni jak w oryginale


def test_copy_inherits_payment_status_as_initial_payment_made_today():
    copy = _copy()  # oryginał: partially_paid, wpłacone 50

    assert copy.payment_status == "partially_paid"
    assert copy.paid_date == TODAY
    assert copy.paid_amount == Decimal("50")


def test_copy_of_unpaid_record_has_no_initial_payment():
    from dataclasses import replace

    service = RecordEditWorkspaceQueryService(
        contract_query_service=None,
        contract_tree_query_service=None,
        value_type_query_service=None,
        today=lambda: TODAY,
    )
    copy = service._as_copy(replace(_source(), payment_status="unpaid", paid_amount=Decimal("0"), payments=[]))

    assert copy.payment_status == "unpaid"
    assert copy.paid_date is None
    assert copy.paid_amount == Decimal("0")
