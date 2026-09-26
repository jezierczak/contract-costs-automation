from datetime import date

import pytest

from contract_costs.model.financial_record import PaymentMethod, PaymentStatus
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import (
    DocumentParseNormalizer,
)


def _normalize_record(**record):
    payload = {"record": {"reference": "FV/1", "invoice_date": "2026-09-15", **record}}
    return DocumentParseNormalizer().normalize_payload(payload).record


@pytest.mark.parametrize("method", ["cash", "card", "blik", "bon", "pre_paid"])
@pytest.mark.parametrize("parsed_status", [None, "unpaid", "unknown"])
def test_settled_at_sale_methods_are_always_paid(method, parsed_status):
    record = _normalize_record(payment_method=method, payment_status=parsed_status)

    assert record.payment_method == PaymentMethod(method)
    assert record.payment_status == PaymentStatus.PAID
    assert record.paid_date == date(2026, 9, 15)


def test_paid_date_from_document_wins_over_invoice_date():
    record = _normalize_record(payment_method="cash", paid_date="2026-09-16")

    assert record.paid_date == date(2026, 9, 16)


def test_paid_bank_transfer_without_paid_date_gets_invoice_date():
    record = _normalize_record(payment_method="bank_transfer", payment_status="paid")

    assert record.payment_status == PaymentStatus.PAID
    assert record.paid_date == date(2026, 9, 15)


@pytest.mark.parametrize(
    "parsed_status, expected",
    [("unpaid", PaymentStatus.UNPAID), (None, PaymentStatus.UNKNOWN)],
)
def test_bank_transfer_keeps_parsed_status(parsed_status, expected):
    record = _normalize_record(payment_method="bank_transfer", payment_status=parsed_status)

    assert record.payment_status == expected
    assert record.paid_date is None
