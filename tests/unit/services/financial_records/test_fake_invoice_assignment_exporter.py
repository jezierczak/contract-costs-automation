from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

from contract_costs.services.financial_records.assigment.prepare.export.fake_invoice_assignment_exporter import (
    FakeInvoiceAssignmentExporter,
)


def test_fake_invoice_assignment_exporter_keeps_last_bundle() -> None:
    exporter = FakeInvoiceAssignmentExporter()
    bundle = Mock()

    exporter.export(
        organization_id=uuid4(),
        bundle=bundle,
        output_path=Path("out.xlsx"),
    )

    assert exporter.bundle is bundle

