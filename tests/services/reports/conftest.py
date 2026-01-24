from datetime import datetime
from decimal import Decimal
from uuid import uuid4
import pytest

from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.model.invoice import Invoice, InvoiceStatus, PaymentMethod, PaymentStatus
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.unit_of_measure import UnitOfMeasure

from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.contract_node_repository import InMemoryContractNodeRepository
from contract_costs.repository.inmemory.value_type_repository import InMemoryValueTypeRepository
from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository

from contract_costs.services.reports.contract_cost_report_service import (
    ContractCostReportService,
)

@pytest.fixture
def contract():
    return Contract(
        id=uuid4(),
        code="C1",
        name="Test contract",
        owner=None,
        client=None,
        description=None,
        start_date=None,
        end_date=None,
        budget=None,
        path=None,
        status=None,
    )


@pytest.fixture
def cost_nodes(contract):
    root = ContractNode(
        id=uuid4(),
        contract_id=contract.id,
        code="ROOT",
        name="Root",
        parent_id=None,
        quantity=None,
        unit=None,
        budget=None,
        is_active=True,
        progress=None
    )

    leaf = ContractNode(
        id=uuid4(),
        contract_id=contract.id,
        code="MAT",
        name="Materials",
        parent_id=root.id,
        quantity=None,
        unit=None,
        budget=None,
        is_active=True,
        progress=Decimal("0.5"),
    )

    return root, leaf


@pytest.fixture
def value_type():
    return ValueType(
        id=uuid4(),
        code="MATERIAL",
        name="Material",
        description=None,
        direction=ValueDirection.COST,
        is_active=True,
    )

@pytest.fixture
def invoice(contract):
    return Invoice(
        id=uuid4(),
        invoice_number="FV/1",
        invoice_date=None,
        selling_date=None,
        buyer_id=uuid4(),
        seller_id=uuid4(),
        payment_method=PaymentMethod.BANK_TRANSFER,
        due_date=None,
        paid_date=None,
        payment_status=PaymentStatus.UNPAID,
        status=InvoiceStatus.PROCESSED,
        timestamp=datetime.now(),
        scan_filename=None,
        tags=set(),
    )


@pytest.fixture
def invoice_line(contract, invoice, cost_nodes, value_type):
    _, leaf = cost_nodes

    return InvoiceLine(
        id=uuid4(),
        invoice_id=invoice.id,
        item_name="Cement",
        description=None,
        quantity=Decimal("1"),
        unit=UnitOfMeasure.PIECE,
        amount=Amount(Decimal("100"), VatRate.VAT_23),
        contract_id=contract.id,          # ważne: kontrakt
        contract_node_id=leaf.id,             # tylko LIŚĆ
        value_type_id=value_type.id,
    )


@pytest.fixture
def report_service(contract, cost_nodes, value_type, invoice, invoice_line):
    contract_repo = InMemoryContractRepository()
    cost_node_repo = InMemoryContractNodeRepository()
    cost_type_repo = InMemoryValueTypeRepository()
    invoice_repo = InMemoryInvoiceRepository()
    invoice_line_repo = InMemoryInvoiceLineRepository()

    contract_repo.add(contract)
    for n in cost_nodes:
        cost_node_repo.add(n)

    cost_type_repo.add(value_type)
    invoice_repo.add(invoice)
    invoice_line_repo.add(invoice_line)

    return ContractCostReportService(
        contract_repo,
        invoice_line_repo,
        cost_node_repo,
        cost_type_repo,
    )
