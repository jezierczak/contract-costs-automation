from uuid import uuid4

from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.services.value_types.query.value_type_query_service import ValueTypeQuery
from contract_costs.services.value_types.query.value_type_query_service import (
    ValueTypeQueryService,
)


def test_query_returns_only_active_by_default(repo):
    repo.add(ValueType(uuid4(), "A", "Active", None,ValueDirection.COST, True))
    repo.add(ValueType(uuid4(), "I", "Inactive", None,ValueDirection.COST, False))

    service = ValueTypeQueryService(repo)
    result = service.list(ValueTypeQuery())

    assert len(result) == 1
    assert result[0].is_active is True


def test_query_include_inactive(repo):
    repo.add(ValueType(uuid4(), "A", "Active", None,ValueDirection.COST, True))
    repo.add(ValueType(uuid4(), "I", "Inactive", None,ValueDirection.COST, False))

    service = ValueTypeQueryService(repo)
    result = service.list(ValueTypeQuery(include_inactive=True))

    assert len(result) == 2


def test_query_code_filter(repo):
    repo.add(ValueType(uuid4(), "MAT", "Material", None,ValueDirection.COST, True))
    repo.add(ValueType(uuid4(), "SAL", "Salary", None,ValueDirection.COST, True))

    service = ValueTypeQueryService(repo)
    result = service.list(ValueTypeQuery(code="MAT"))

    assert len(result) == 1
    assert result[0].code == "MAT"


def test_query_search(repo):
    repo.add(ValueType(uuid4(), "A", "Office materials", "Paper",ValueDirection.COST, True))
    repo.add(ValueType(uuid4(), "B", "Salary", "Monthly payroll",ValueDirection.COST, True))

    service = ValueTypeQueryService(repo)
    result = service.list(ValueTypeQuery(search="paper"))

    assert len(result) == 1
    assert "Paper" in result[0].description
