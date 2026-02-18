from uuid import uuid4
from unittest.mock import MagicMock

from contract_costs.model.company import CompanyType
from tests.builders.company_builder import CompanyBuilder
from contract_costs.services.contracts.migration.back_fill_system_contracts_service import (
    BackfillSystemContractsService,
)
from contract_costs.services.contracts.migration.backfill_system_contracts_command import (
    BackfillSystemContractsCommand,
)


def test_execute_calls_create_system_for_each_owner(uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    owners = [
        CompanyBuilder().with_organization_id(organization_id).with_role(CompanyType.OWN).build(),
        CompanyBuilder().with_organization_id(organization_id).with_role(CompanyType.OWN).build(),
    ]
    for owner in owners:
        uow.companies.add(owner)

    create_system = MagicMock()

    service = BackfillSystemContractsService(
        create_system_contract=create_system,
    )

    service.execute(
        action=BackfillSystemContractsCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        ),
        uow=uow,
    )
    assert create_system.execute.call_count == 2

    first_call = create_system.execute.call_args_list[0].kwargs
    second_call = create_system.execute.call_args_list[1].kwargs

    assert first_call["organization_id"] == organization_id
    assert first_call["actor_user_id"] == actor_user_id
    assert first_call["owner"] == owners[0]
    assert first_call["uow"] is uow

    assert second_call["organization_id"] == organization_id
    assert second_call["actor_user_id"] == actor_user_id
    assert second_call["owner"] == owners[1]
    assert second_call["uow"] is uow


def test_execute_does_not_call_create_system_when_no_owners(uow):
    create_system = MagicMock()

    service = BackfillSystemContractsService(
        create_system_contract=create_system,
    )

    service.execute(
        action=BackfillSystemContractsCommand(
            organization_id=uuid4(),
            actor_user_id=uuid4(),
        ),
        uow=uow,
    )

    create_system.execute.assert_not_called()
