from datetime import datetime
from uuid import uuid4

import pytest

from contract_costs.model.company import CompanyType
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.companies.dto.create_company_command import CreateOwnerCompanyCommand
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork


class _FakeCreateSystemContract:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)
        if self.should_fail:
            raise RuntimeError("boom")


def _owner_cmd():
    return CreateOwnerCompanyCommand(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        name="ACME",
        description=None,
        tax_number="PL 123-456-32-18",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.OWN,
        tags=None,
    )


def test_create_company_uses_uow_and_calls_system_orchestrator():
    uow = InMemoryUnitOfWork()
    create_system = _FakeCreateSystemContract()
    service = CreateCompanyService(
        create_system_contract=create_system,
        id_generator=lambda: uuid4(),
        clock=lambda: datetime(2026, 2, 16, 12, 0, 0),
    )

    cmd = _owner_cmd()
    company = service.execute(action=cmd, uow=uow)

    persisted = uow.companies.get(company.id, cmd.organization_id)
    assert persisted is not None
    assert len(create_system.calls) == 1
    assert create_system.calls[0]["uow"] is uow


def test_create_company_propagates_orchestrator_failure():
    uow = InMemoryUnitOfWork()
    service = CreateCompanyService(
        create_system_contract=_FakeCreateSystemContract(should_fail=True),
    )

    with pytest.raises(RuntimeError, match="boom"):
        service.execute(action=_owner_cmd(), uow=uow)
