from uuid import uuid4

from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.value_types.query.dto.value_type_query import ValueTypeQuery
from contract_costs.services.value_types.query.value_type_query_service import (
    ValueTypeQueryService,
)
from tests.builders.value_type_builder import ValueTypeBuilder


def _query(organization_id, **kwargs):
    return ValueTypeQuery(
        organization_id=organization_id,
        actor_user_id=kwargs.get("actor_user_id", uuid4()),
        code=kwargs.get("code"),
        direction=kwargs.get("direction"),
        include_inactive=kwargs.get("include_inactive", False),
        search=kwargs.get("search"),
    )


def test_query_filters_active_direction_code_and_search(value_type_repo, uow):
    organization_id = uuid4()

    active_cost = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_code("MAT")
        .with_direction(ValueDirection.COST)
        .with_is_active(True)
        .build()
    )
    active_cost.name = "Material cost"
    inactive_cost = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_code("OLD")
        .with_direction(ValueDirection.COST)
        .with_is_active(False)
        .build()
    )
    inactive_cost.name = "Legacy category"
    active_revenue = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_code("REV")
        .with_direction(ValueDirection.REVENUE)
        .with_is_active(True)
        .build()
    )
    active_revenue.name = "Revenue stream"

    value_type_repo.add(active_cost)
    value_type_repo.add(inactive_cost)
    value_type_repo.add(active_revenue)

    service = ValueTypeQueryService()

    result_active_only = service.execute(action=_query(organization_id), uow=uow)
    assert {x.code for x in result_active_only} == {"MAT", "REV"}

    result_cost_only = service.execute(
        action=_query(
            organization_id,
            direction="COST",
            include_inactive=True,
        ),
        uow=uow,
    )
    assert {x.code for x in result_cost_only} == {"MAT", "OLD"}

    result_code = service.execute(
        action=_query(
            organization_id,
            code="REV",
            include_inactive=True,
        ),
        uow=uow,
    )
    assert [x.code for x in result_code] == ["REV"]

    result_search = service.execute(
        action=_query(
            organization_id,
            search="material",
            include_inactive=True,
        ),
        uow=uow,
    )
    assert [x.code for x in result_search] == ["MAT"]


def test_query_maps_direction_to_string_in_dto(value_type_repo, uow):
    organization_id = uuid4()
    value_type = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_direction(ValueDirection.REVENUE)
        .with_code("R-1")
        .build()
    )
    value_type_repo.add(value_type)

    service = ValueTypeQueryService()

    result = service.execute(
        action=_query(organization_id, include_inactive=True),
        uow=uow,
    )

    assert len(result) == 1
    assert result[0].direction == "REVENUE"
