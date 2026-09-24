from datetime import date
from decimal import Decimal
from uuid import uuid4

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.amount import Amount, AmountInputType, VatRate
from contract_costs.model.contract import ContractType
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_service import \
    ListContractsQueryService
from tests.builders.contract_builder import ContractBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from tests.builders.value_type_builder import ValueTypeBuilder


def test_returns_empty_list_when_no_contracts(
    contract_repo,
    contract_node_repo,
    line_repo,
    value_type_repo,
    uow,
):
    service = ListContractsQueryService()

    result = service.execute(
        action=ListContractsQuery(
            organization_id=uuid4(),
            actor_user_id=uuid4(),
            contract_type=ContractType.PROJECT,
        ),
        uow=uow,
    )

    assert result == []

def test_planned_budget_and_progress_calculation(
    contract_repo,
    contract_node_repo,
    line_repo,
    value_type_repo,
    uow,
):
    organization_id = uuid4()

    contract = (
        ContractBuilder()
        .with_organization_id(organization_id)
        .build()
    )
    contract_repo.add(contract)

    root = ContractNode(
        id=new_uuid(),
        organization_id=organization_id,
        contract_id=contract.id,
        parent_id=None,
        code="ROOT",
        name="Root",
        budget=None,
        quantity=None,
        unit=None,
        is_active=True,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        progress_history={},
    )

    leaf_a = ContractNode(
        id=new_uuid(),
        organization_id=organization_id,
        contract_id=contract.id,
        parent_id=root.id,
        code="A",
        name="A",
        budget=Decimal("100"),
        quantity=None,
        unit=None,
        is_active=True,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        progress_history={date.today(): Decimal("0.5")},
    )

    leaf_b = ContractNode(
        id=new_uuid(),
        organization_id=organization_id,
        contract_id=contract.id,
        parent_id=root.id,
        code="B",
        name="B",
        budget=Decimal("300"),
        quantity=None,
        unit=None,
        is_active=True,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        progress_history={date.today(): Decimal("1.0")},
    )

    contract_node_repo.add_all([root, leaf_a, leaf_b])

    service = ListContractsQueryService()

    result = service.execute(
        action=ListContractsQuery(
            organization_id=organization_id,
            actor_user_id=uuid4(),
            contract_type=ContractType.PROJECT,
        ),
        uow=uow,
    )

    dto = result[0]

    assert dto.planned_budget == Decimal("400")
    assert dto.progress == Decimal("0.875")  # (100*0.5 + 300*1.0)/400


def test_financial_aggregation(
    contract_repo,
    contract_node_repo,
    line_repo,
    value_type_repo,
    uow,
):
    organization_id = uuid4()

    cost_type = (
        ValueTypeBuilder()
        .with_direction(ValueDirection.COST)
        .with_organization_id(organization_id)
        .build()
    )

    revenue_type = (
        ValueTypeBuilder()
        .with_direction(ValueDirection.REVENUE)
        .with_organization_id(organization_id)
        .build()
    )

    value_type_repo.add(cost_type)
    value_type_repo.add(revenue_type)

    contract = (
        ContractBuilder()
        .with_organization_id(organization_id)
        .build()
    )
    contract_repo.add(contract)

    root = ContractNode(
        id=new_uuid(),
        organization_id=organization_id,
        contract_id=contract.id,
        parent_id=None,
        code="ROOT",
        name="Root",
        budget=None,
        quantity=None,
        unit=None,
        is_active=True,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        progress_history={},
    )

    contract_node_repo.add(root)

    # COST 100
    line_repo.add(
        organization_id=organization_id,
        line=(
            FinancialRecordLineBuilder()
            .with_organization_id(organization_id)
            .with_contract_id(contract.id)
            .with_value_type_id(cost_type.id)
            .with_amount(Amount(value=Decimal("100"), input_type=AmountInputType.NET, vat_rate=VatRate.VAT_23))
            .build()
        ),
    )

    # REVENUE 200
    line_repo.add(
        organization_id=organization_id,
        line=(
            FinancialRecordLineBuilder()
            .with_organization_id(organization_id)
            .with_contract_id(contract.id)
            .with_value_type_id(revenue_type.id)
            .with_amount(Amount(value=Decimal("200"), input_type=AmountInputType.NET, vat_rate=VatRate.VAT_23))
            .build()
        ),
    )

    service = ListContractsQueryService()

    result = service.execute(
        action=ListContractsQuery(
            organization_id=organization_id,
            actor_user_id=uuid4(),
            contract_type=ContractType.PROJECT,
        ),
        uow=uow,
    )

    dto = result[0]

    assert dto.net == Decimal("100")
    assert dto.revenue == Decimal("200")


def test_contract_without_nodes_shows_up_with_zero_values(
    contract_repo,
    contract_node_repo,
    line_repo,
    value_type_repo,
    uow,
):
    """
    Kontrakt bez jeszcze zbudowanych węzłów (same metadane) ma się pojawiać
    na liście z zerowymi wartościami finansowymi, a nie być pomijany.
    """
    organization_id = uuid4()

    contract = (
        ContractBuilder()
        .with_organization_id(organization_id)
        .build()
    )
    contract_repo.add(contract)

    service = ListContractsQueryService()

    result = service.execute(
        action=ListContractsQuery(
            organization_id=organization_id,
            actor_user_id=uuid4(),
            contract_type=ContractType.PROJECT,
        ),
        uow=uow,
    )

    assert len(result) == 1
    dto = result[0]
    assert dto.contract_id == contract.id
    assert dto.net == Decimal("0")
    assert dto.revenue == Decimal("0")
