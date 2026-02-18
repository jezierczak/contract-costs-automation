import pytest

from contract_costs.services.identity.add.create_organization_with_owner import (
    CreateOrganizationWithOwnerService,
)
from contract_costs.services.identity.add.dto.create_organization_command import (
    CreateOrganizationCommand,
)
from contract_costs.services.identity.exceptions import OrganizationAlreadyExists
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork


class _FakeInitAppService:
    def __init__(self):
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)


def _cmd() -> CreateOrganizationCommand:
    return CreateOrganizationCommand(
        organization_code="ORG-1",
        organization_name="Org",
        owner_login="owner",
        owner_email="owner@example.com",
        owner_full_name="Owner",
        created_by_user_id=None,
    )


def test_create_organization_with_owner_uses_uow():
    uow = InMemoryUnitOfWork()
    init_app = _FakeInitAppService()
    service = CreateOrganizationWithOwnerService(init_app_service=init_app)

    org_id = service.execute(action=_cmd(), uow=uow)

    assert uow.organizations.get(org_id) is not None


def test_create_organization_with_owner_rejects_duplicate_code():
    uow = InMemoryUnitOfWork()
    service = CreateOrganizationWithOwnerService(init_app_service=_FakeInitAppService())

    service.execute(action=_cmd(), uow=uow)

    with pytest.raises(OrganizationAlreadyExists):
        service.execute(action=_cmd(), uow=uow)
