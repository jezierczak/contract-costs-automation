from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from contract_costs.services.financial_records.review.dto.document_view import DocumentView
from contract_costs.services.financial_records.review.dto.invoice_for_accountant_view import (
    InvoiceForAccountantView,
)


def test_invoice_for_accountant_view_validates_model() -> None:
    view = InvoiceForAccountantView(
        invoice_id=uuid4(),
        invoice_number="FV/1/2026",
        invoice_date=date(2026, 2, 17),
        buyer_name="Buyer",
        buyer_tax_number="123",
        seller_name="Seller",
        seller_tax_number="456",
        total_net=Decimal("100"),
        total_vat=Decimal("23"),
        total_gross=Decimal("123"),
        total_not_evidenced=Decimal("0"),
        documents=[DocumentView(filename="a.pdf", file_path="p/a.pdf", document_type_="invoice")],
    )
    assert view.invoice_number == "FV/1/2026"
    assert view.total_gross == Decimal("123")


def test_invoice_for_accountant_view_rejects_invalid_document_shape() -> None:
    with pytest.raises(ValidationError):
        InvoiceForAccountantView(
            invoice_id=uuid4(),
            invoice_number="FV/1/2026",
            invoice_date=None,
            buyer_name="Buyer",
            buyer_tax_number="123",
            seller_name="Seller",
            seller_tax_number="456",
            total_net=Decimal("100"),
            total_vat=Decimal("23"),
            total_gross=Decimal("123"),
            total_not_evidenced=Decimal("0"),
            documents=[{"filename": "a.pdf"}],
        )

