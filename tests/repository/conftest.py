from decimal import Decimal
from uuid import uuid4
from datetime import date, datetime

import pytest

from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.cost_type import CostType
from contract_costs.model.invoice import Invoice, InvoiceStatus, PaymentMethod, PaymentStatus
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.unit_of_measure import UnitOfMeasure


@pytest.fixture
def invoice_new(contract_owner, contract_company):
    return Invoice(
        id=uuid4(),
        invoice_number="FV/1",
        invoice_date=date.today(),
        selling_date=date.today(),
        buyer_id=contract_owner.id,
        seller_id=contract_company.id,

        payment_method=PaymentMethod.CASH,
        due_date=date.today(),
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.NEW,
        timestamp=datetime.now(),
    )


@pytest.fixture
def invoice_in_progress(contract_owner, contract_company):
    return Invoice(
        id=uuid4(),
        invoice_number="FV/2",
        invoice_date=date.today(),
        selling_date=date.today(),
        buyer_id=contract_owner.id,
        seller_id=contract_company.id,

        payment_method=PaymentMethod.CARD,
        due_date=date.today(),
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.IN_PROGRESS,
        timestamp=datetime.now(),
    )


@pytest.fixture
def invoice_processed(contract_owner, contract_company):
    return Invoice(
        id=uuid4(),
        invoice_number="FV/3",
        invoice_date=date.today(),
        selling_date=date.today(),
        buyer_id=contract_owner.id,
        seller_id=contract_company.id,

        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=date.today(),
        payment_status=PaymentStatus.PAID,
        status=InvoiceStatus.PROCESSED,
        timestamp=datetime.now(),
    )

@pytest.fixture
def contract_id_1():
    return uuid4()


@pytest.fixture
def contract_id_2():
    return uuid4()


@pytest.fixture
def invoice_line_complete(contract_id_1):
    return InvoiceLine(
        id=uuid4(),
        invoice_id=uuid4(),
        quantity=Decimal("1"),
        unit=UnitOfMeasure.PIECE,
        amount=Amount(Decimal("100"), VatRate.VAT_23),
        contract_id=contract_id_1,
        cost_node_id=uuid4(),
        cost_type_id=uuid4(),
        description="Complete line",
    )


@pytest.fixture
def invoice_line_missing_cost_node(contract_id_1):
    return InvoiceLine(
        id=uuid4(),
        invoice_id=uuid4(),
        quantity=Decimal("1"),
        unit=UnitOfMeasure.SERVICE,
        amount=Amount(Decimal("50"), VatRate.VAT_8),
        contract_id=contract_id_1,
        cost_node_id=None,
        cost_type_id=uuid4(),
        description="Missing cost node",
    )


@pytest.fixture
def invoice_line_missing_cost_type(contract_id_2):
    return InvoiceLine(
        id=uuid4(),
        invoice_id=uuid4(),
        quantity=Decimal("2"),
        unit=UnitOfMeasure.HOUR,
        amount=Amount(Decimal("200"), VatRate.VAT_23),
        contract_id=contract_id_2,
        cost_node_id=uuid4(),
        cost_type_id=None,
        description="Missing cost type",
    )

@pytest.fixture
def cost_type_material():
    return CostType(
        id=uuid4(),
        code="MAT",
        name="Material",
        is_active=True,
    )


@pytest.fixture
def cost_type_service():
    return CostType(
        id=uuid4(),
        code="SRV",
        name="Service",
        is_active=True,
    )

from uuid import uuid4
from datetime import date
import pytest

from contract_costs.model.cost_progress_snapshot import CostProgressSnapshot


@pytest.fixture
def contract_id():
    return uuid4()


@pytest.fixture
def cost_node_id():
    return uuid4()


@pytest.fixture
def snapshot_1(contract_id, cost_node_id):
    return CostProgressSnapshot(
        id=uuid4(),
        contract_id=contract_id,
        cost_node_id=cost_node_id,
        snapshot_date=date(2024, 1, 1),
        planned_amount=Decimal("100"),
        executed_amount=Decimal("25"),
        progress_percent=Decimal("0.25"),
    )


@pytest.fixture
def snapshot_2(contract_id, cost_node_id):
    return CostProgressSnapshot(
        id=uuid4(),
        contract_id=contract_id,
        cost_node_id=cost_node_id,
        snapshot_date=date(2024, 2, 1),
        planned_amount=Decimal("200"),
        executed_amount=Decimal("100"),
        progress_percent=Decimal("0.50"),
    )


@pytest.fixture
def snapshot_other_node(contract_id):
    return CostProgressSnapshot(
        id=uuid4(),
        contract_id=contract_id,
        cost_node_id=None,
        snapshot_date=date(2024, 3, 1),
        planned_amount=Decimal("400"),
        executed_amount=Decimal("300"),
        progress_percent=Decimal("0.75"),
    )
