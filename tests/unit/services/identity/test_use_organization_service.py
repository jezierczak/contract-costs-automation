from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.organization_user_builder import OrganizationUserBuilder
from contract_costs.services.identity.exceptions import (
    OrganizationNotFound,
    UserNotMemberOfOrganization,
)
from contract_costs.services.identity.use.dto.use_organization_command import (
    UseOrganizationCommand,
)
from contract_costs.services.identity.use.use_organization_service import (
    UseOrganizationService,
)


def test_use_organization_service_sets_context_on_success() -> None:
    actor_id = uuid4()
    org = OrganizationBuilder().with_id(uuid4()).with_code("ORG1").build()
    membership = (
        OrganizationUserBuilder()
        .with_organization_id(org.id)
        .with_user_id(actor_id)
        .with_is_active(True)
        .build()
    )

    context = Mock()
    uow = SimpleNamespace(
        organizations=SimpleNamespace(get_by_code=lambda code: org if code == "ORG1" else None),
        organization_users=SimpleNamespace(
            get_by_org_and_user=lambda **_: membership
        ),
    )
    action = UseOrganizationCommand(
        actor_user_id=actor_id,
        organization_code="ORG1",
    )

    UseOrganizationService(context=context).execute(action=action, uow=uow)
    context.set_current_organization.assert_called_once_with(org.id)


def test_use_organization_service_raises_for_missing_or_inactive_org() -> None:
    actor_id = uuid4()
    inactive = OrganizationBuilder().inactive().with_code("INACTIVE").build()
    context = Mock()

    uow = SimpleNamespace(
        organizations=SimpleNamespace(get_by_code=lambda code: None if code == "MISS" else inactive),
        organization_users=SimpleNamespace(get_by_org_and_user=lambda **_: None),
    )

    with pytest.raises(OrganizationNotFound):
        UseOrganizationService(context=context).execute(
                action=UseOrganizationCommand(
                    actor_user_id=actor_id,
                    organization_code="MISS",
                ),
            uow=uow,
        )

    with pytest.raises(OrganizationNotFound):
        UseOrganizationService(context=context).execute(
                action=UseOrganizationCommand(
                    actor_user_id=actor_id,
                    organization_code="INACTIVE",
                ),
            uow=uow,
        )


def test_use_organization_service_raises_for_missing_or_inactive_membership() -> None:
    actor_id = uuid4()
    org = OrganizationBuilder().with_id(uuid4()).with_code("ORG1").build()
    inactive_member = OrganizationUserBuilder().with_is_active(False).build()
    context = Mock()

    uow_missing = SimpleNamespace(
        organizations=SimpleNamespace(get_by_code=lambda _code: org),
        organization_users=SimpleNamespace(get_by_org_and_user=lambda **_: None),
    )
    uow_inactive = SimpleNamespace(
        organizations=SimpleNamespace(get_by_code=lambda _code: org),
        organization_users=SimpleNamespace(get_by_org_and_user=lambda **_: inactive_member),
    )

    with pytest.raises(UserNotMemberOfOrganization):
        UseOrganizationService(context=context).execute(
                action=UseOrganizationCommand(
                    actor_user_id=actor_id,
                    organization_code="ORG1",
                ),
            uow=uow_missing,
        )

    with pytest.raises(UserNotMemberOfOrganization):
        UseOrganizationService(context=context).execute(
                action=UseOrganizationCommand(
                    actor_user_id=actor_id,
                    organization_code="ORG1",
                ),
            uow=uow_inactive,
        )
