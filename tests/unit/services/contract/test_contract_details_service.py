import pytest
from decimal import Decimal
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.contract import ContractStatus
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.contract_node_progress import ContractNodeProgress
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.contracts.query.contract_details.contract_details_query_service import (
    ContractDetailsQueryService,
)
from contract_costs.services.contracts.query.contract_details.contract_details_query_command import (
    ContractDetailsQuery,
)

from tests.builders.contract_builder import ContractBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from tests.builders.value_type_builder import ValueTypeBuilder


def test_contract_not_found_raises(
    contract_repo,
    contract_node_repo,
    line_repo,
    value_type_repo,
    uow,
):
    service = ContractDetailsQueryService()

    query = ContractDetailsQuery(
        organization_id=uuid4(),
        contract_id=uuid4(),
        at_date=None,
        actor_user_id=uuid4()
    )

    with pytest.raises(ValueError, match="Contract not found"):
        service.execute(action=query, uow=uow)


def test_budget_and_progress_rollup(
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
        .with_status(ContractStatus.ACTIVE)
        .build()
    )
    contract_repo.add(contract)

    # ROOT
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

    # LEAF A
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
        progress_history={},
    )

    # leaf_a.add_progress(
    #     progress=Decimal("0.5"),
    #     progress_date=date.today(),
    #     organization_id=organization_id,
    # )

    # LEAF B
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
        progress_history={},
    )

    # leaf_b.add_progress(
    #     progress=Decimal("1.0"),
    #     progress_date=date.today(),
    #     organization_id=organization_id,
    # )

    contract_node_repo.add_all([root, leaf_a, leaf_b])

    contract_node_repo.add_progress(
        ContractNodeProgress(
            id=new_uuid(),
            organization_id=organization_id,
            contract_node_id=leaf_a.id,
            progress=Decimal("0.5"),
            progress_date=date.today(),
            created_at=utc_now(),
            created_by_user_id=None,
            updated_at=None,
            updated_by_user_id=None,
        )
    )

    contract_node_repo.add_progress(
        ContractNodeProgress(
            id=new_uuid(),
            organization_id=organization_id,
            contract_node_id=leaf_b.id,
            progress=Decimal("1.0"),
            progress_date=date.today(),
            created_at=utc_now(),
            created_by_user_id=None,
            updated_at=None,
            updated_by_user_id=None,
        )
    )

    service = ContractDetailsQueryService()

    result = service.execute(
        action=ContractDetailsQuery(
            organization_id=organization_id,
            contract_id=contract.id,
            at_date=None,
            actor_user_id=uuid4()
        ),
        uow=uow,
    )

    root_dto = next(n for n in result.nodes if n.parent_id is None)

    assert root_dto.planned_budget == Decimal("400")
    assert root_dto.progress == Decimal("0.875")  # (100*0.5 + 300*1.0)/400


def test_financial_rollup(
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

    leaf = ContractNode(
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
        progress_history={},
    )

    contract_node_repo.add_all([root, leaf])

    line_repo.list_by_contract = lambda **kwargs: [
        SimpleNamespace(
            contract_node_code=leaf.id,
            value_type_code=cost_type.id,
            amount=Amount(Decimal("100"), VatRate.VAT_23),
        ),
        SimpleNamespace(
            contract_node_code=leaf.id,
            value_type_code=revenue_type.id,
            amount=Amount(Decimal("200"), VatRate.VAT_23),
        ),
    ]

    service = ContractDetailsQueryService()

    result = service.execute(
        action=ContractDetailsQuery(
            organization_id=organization_id,
            contract_id=contract.id,
            at_date=None,
            actor_user_id=uuid4()
        ),
        uow=uow,
    )

    root_dto = next(n for n in result.nodes if n.parent_id is None)

    assert root_dto.net == Decimal("100")
    assert root_dto.revenue == Decimal("200")


def test_progress_at_date(
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

    leaf = ContractNode(
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
        progress_history={},
    )


    # leaf.add_progress(Decimal("0.8"), date(2024, 6, 1), organization_id)
    contract_node_repo.add_all([root, leaf])

    contract_node_repo.add_progress(
        ContractNodeProgress(
            id=new_uuid(),
            organization_id=organization_id,
            contract_node_id=leaf.id,
            progress=Decimal("0.2"),
            progress_date= date(2024, 1, 1),
            created_at=utc_now(),
            created_by_user_id=None,
            updated_at=None,
            updated_by_user_id=None,
        )
    )

    contract_node_repo.add_progress(
        ContractNodeProgress(
            id=new_uuid(),
            organization_id=organization_id,
            contract_node_id=leaf.id,
            progress=Decimal("0.8"),
            progress_date=date(2024, 6, 1),
            created_at=utc_now(),
            created_by_user_id=None,
            updated_at=None,
            updated_by_user_id=None,
        )
    )


    contract_node_repo.add_all([root, leaf])

    service = ContractDetailsQueryService()

    result = service.execute(
        action=ContractDetailsQuery(
            organization_id=organization_id,
            contract_id=contract.id,
            at_date=date(2024, 2, 1),
            actor_user_id=uuid4()
        ),
        uow=uow,
    )

    leaf_dto = next(n for n in result.nodes if n.code == "A")

    assert leaf_dto.progress == Decimal("0.2")
