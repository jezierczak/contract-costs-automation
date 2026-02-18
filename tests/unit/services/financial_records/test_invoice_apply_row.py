from uuid import uuid4

import pytest
from pydantic import ValidationError

from contract_costs.services.financial_records.actions.dto.invoice_apply_row import (
    InvoiceApplyRow,
)


def test_invoice_apply_row_accepts_valid_data() -> None:
    row = InvoiceApplyRow(invoice_id=uuid4(), selected=True)
    assert row.selected is True


def test_invoice_apply_row_requires_uuid() -> None:
    with pytest.raises(ValidationError):
        InvoiceApplyRow(invoice_id="not-a-uuid", selected=True)

