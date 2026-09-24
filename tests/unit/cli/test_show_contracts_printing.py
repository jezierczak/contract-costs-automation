"""
Wydruk `show contracts` (lista, drzewo, oś czasu) na danych in-memory —
pilnuje, żeby kolumny CLI nie rozjechały się z DTO kontraktów.
"""
from datetime import date
from decimal import Decimal
from uuid import uuid4

from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.amount import Amount, AmountInputType, VatRate
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.value_direction import ValueDirection
from contract_costs.reports.contracts.contract_list_columns import contract_list_columns
from contract_costs.reports.contracts.contract_node_tree_column import contract_node_tree_columns
from contract_costs.reports.contracts.contract_timeline_columns import contract_timeline_columns
from contract_costs.services.contracts.query.contract_details.contract_details_query_command import (
    ContractDetailsQuery,
)
from contract_costs.services.contracts.query.contract_details.contract_details_query_service import (
    ContractDetailsQueryService,
)
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_service import (
    ListContractsQueryService,
)
from tests.builders.contract_builder import ContractBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from tests.builders.value_type_builder import ValueTypeBuilder

TODAY = date(2026, 3, 15)


def _seed(uow):
    org_id = uuid4()
    cost_type = ValueTypeBuilder().with_organization_id(org_id).with_direction(ValueDirection.COST).build()
    uow.value_types.add(cost_type)

    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_code("K-001")
        .with_start_date(date(2026, 1, 1))
        .with_end_date(date(2026, 12, 31))
        .build()
    )
    uow.contracts.add(contract)

    node = ContractNode(
        id=new_uuid(),
        organization_id=org_id,
        contract_id=contract.id,
        parent_id=None,
        code="A",
        name="Roboty",
        budget=Decimal("1000"),
        quantity=None,
        unit=None,
        is_active=True,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        progress_history={date(2026, 2, 28): Decimal("0.3")},
    )
    uow.contract_nodes.add(node)

    record = FinancialRecordBuilder().with_organization_id(org_id).with_selling_date(date(2026, 2, 10)).build()
    uow.financial_records.add(record)
    uow.financial_record_lines.add(
        organization_id=org_id,
        line=(
            FinancialRecordLineBuilder()
            .with_organization_id(org_id)
            .with_financial_record_id(record.id)
            .with_contract_id(contract.id)
            .with_contract_node_id(node.id)
            .with_value_type_id(cost_type.id)
            .with_amount(Amount(value=Decimal("250"), input_type=AmountInputType.NET, vat_rate=VatRate.VAT_23))
            .build()
        ),
    )
    return org_id, contract


def test_list_prints_financial_columns(uow, capsys):
    org_id, contract = _seed(uow)

    items = ListContractsQueryService(today=lambda: TODAY).execute(
        action=ListContractsQuery(organization_id=org_id, actor_user_id=uuid4()),
        uow=uow,
    )
    CmdPrinter().print(organization_id=str(org_id), items=items, columns=contract_list_columns())

    out = capsys.readouterr().out
    assert "K-001" in out
    assert "RESULT ON PROGRESS" in out
    assert "50,00" in out  # wykonane 300 − koszty 250


def test_details_prints_tree_and_timeline(uow, capsys):
    org_id, contract = _seed(uow)

    details = ContractDetailsQueryService(today=lambda: TODAY).execute(
        action=ContractDetailsQuery(organization_id=org_id, actor_user_id=uuid4(), contract_id=contract.id),
        uow=uow,
    )
    CmdPrinter().print(organization_id=str(org_id), items=details.nodes, columns=contract_node_tree_columns())
    CmdPrinter().print(organization_id=str(org_id), items=details.timeline.months, columns=contract_timeline_columns())

    out = capsys.readouterr().out
    assert "Roboty" in out
    assert "2026-01" in out and "2026-03" in out
    assert "250,00" in out
