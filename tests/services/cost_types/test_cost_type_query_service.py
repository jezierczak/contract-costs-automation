from uuid import uuid4

from contract_costs.model.cost_type import CostType
from contract_costs.services.cost_types.query.cost_type_query_service import CostTypeQuery
from contract_costs.services.cost_types.query.cost_type_query_service import (
    CostTypeQueryService,
)


def test_query_returns_only_active_by_default(repo):
    repo.add(CostType(uuid4(), "A", "Active", None, True))
    repo.add(CostType(uuid4(), "I", "Inactive", None, False))

    service = CostTypeQueryService(repo)
    result = service.list(CostTypeQuery())

    assert len(result) == 1
    assert result[0].is_active is True


def test_query_include_inactive(repo):
    repo.add(CostType(uuid4(), "A", "Active", None, True))
    repo.add(CostType(uuid4(), "I", "Inactive", None, False))

    service = CostTypeQueryService(repo)
    result = service.list(CostTypeQuery(include_inactive=True))

    assert len(result) == 2


def test_query_code_filter(repo):
    repo.add(CostType(uuid4(), "MAT", "Material", None, True))
    repo.add(CostType(uuid4(), "SAL", "Salary", None, True))

    service = CostTypeQueryService(repo)
    result = service.list(CostTypeQuery(code="MAT"))

    assert len(result) == 1
    assert result[0].code == "MAT"


def test_query_search(repo):
    repo.add(CostType(uuid4(), "A", "Office materials", "Paper", True))
    repo.add(CostType(uuid4(), "B", "Salary", "Monthly payroll", True))

    service = CostTypeQueryService(repo)
    result = service.list(CostTypeQuery(search="paper"))

    assert len(result) == 1
    assert "Paper" in result[0].description
