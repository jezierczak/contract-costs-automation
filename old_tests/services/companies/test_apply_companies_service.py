from uuid import uuid4

import pytest
from unittest.mock import MagicMock

from contract_costs.model.company import CompanyType
from contract_costs.services.companies.apply.apply_companies_from_excel_service import ApplyCompaniesFromExcelService
from contract_costs.services.companies.apply.command import ApplyCompanyCommand, CompanyActionType
from contract_costs.services.companies.dto.activate_company_command import BaseActivateCompanyCommand
from contract_costs.services.companies.dto.deactivate_company_command import BaseDeactivateCompanyCommand


@pytest.fixture
def apply_service():
    return ApplyCompaniesFromExcelService(
        create_company_service=MagicMock(),
        update_company_service=MagicMock(),
        activate_company_service=MagicMock(),
        deactivate_company_service=MagicMock(),
    )

@pytest.fixture
def base_command():
    return ApplyCompanyCommand(
        apply_action_type=CompanyActionType.UPDATE,
        company_id=uuid4(),
        tax_number="1234567890",
        name="Company A",
        role=CompanyType.SUPPLIER,
        description=None,
        address_street=None,
        address_city=None,
        address_zip_code=None,
        address_country=None,
        phone_number=None,
        email=None,
        bank_account_number=None,
        bank_account_country_code=None,
        tags=set(),
    )

def test_apply_create_calls_create(apply_service: MagicMock, base_command: ApplyCompanyCommand):
    base_command = base_command.__class__(**{
        **base_command.__dict__,
        "action": CompanyActionType.CREATE,
        "company_id": None,
    })

    apply_service.apply(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        commands=[base_command])

    apply_service._create.execute.assert_called_once()
    apply_service._update.execute.assert_not_called()


def test_apply_update_calls_update(apply_service: MagicMock, base_command: ApplyCompanyCommand):
    apply_service.apply(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        commands=[base_command])

    apply_service._update.execute.assert_called_once()
    apply_service._create.execute.assert_not_called()


def test_apply_activate_calls_activate(apply_service: MagicMock, base_command: ApplyCompanyCommand):
    cmd = base_command.__class__(**{
        **base_command.__dict__,
        "action": CompanyActionType.ACTIVATE,
    })

    org_id = uuid4()
    user_id = uuid4()

    apply_service.apply(
        organization_id=org_id,
        actor_user_id=user_id,
        commands=[cmd],
    )

    apply_service._activate.execute.assert_called_once()

    called_cmd = apply_service._activate.execute.call_args.args[0]

    assert isinstance(called_cmd, BaseActivateCompanyCommand)
    assert called_cmd.company_id == cmd.company_id
    assert called_cmd.organization_id == org_id
    assert called_cmd.actor_user_id == user_id


def test_apply_deactivate_calls_deactivate(apply_service: MagicMock, base_command: ApplyCompanyCommand):
    cmd = base_command.__class__(**{
        **base_command.__dict__,
        "action": CompanyActionType.DEACTIVATE,
    })
    org_id = uuid4()
    user_id = uuid4()
    apply_service.apply(
        organization_id=org_id,
        actor_user_id=user_id,
        commands=[cmd])

    apply_service._deactivate.execute.assert_called_once()

    called_cmd = apply_service._deactivate.execute.call_args.args[0]

    assert isinstance(called_cmd, BaseDeactivateCompanyCommand)
    assert called_cmd.company_id == cmd.company_id
    assert called_cmd.organization_id == org_id
    assert called_cmd.actor_user_id == user_id


def test_apply_none_action_does_nothing(apply_service: MagicMock, base_command: ApplyCompanyCommand):
    cmd = base_command.__class__(**{
        **base_command.__dict__,
        "action": CompanyActionType.NONE,
    })

    apply_service.apply(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        commands=[cmd])

    apply_service._create.execute.assert_not_called()
    apply_service._update.execute.assert_not_called()
    apply_service._activate.execute.assert_not_called()
    apply_service._deactivate.execute.assert_not_called()


# def test_apply_update_without_company_id_raises(apply_service: MagicMock, base_command: CompanyActionCommand):
#     cmd = base_command.__class__(**{
#         **base_command.__dict__,
#         "company_id": None,
#     })
#
#     with pytest.raises(ValueError):
#         apply_service.apply([cmd])
#
def test_apply_update_without_company_id_raises(apply_service, base_command):
    cmd = base_command.__class__(**{
        **base_command.__dict__,
        "company_id": None,
    })

    with pytest.raises(RuntimeError) as exc_info:
        apply_service.execute(
            organization_id=uuid4(),
            actor_user_id=uuid4(),
            commands=[cmd])

    # sprawdzamy przyczynę
    assert isinstance(exc_info.value.__cause__, ValueError)
    assert "UPDATE requires company_id" in str(exc_info.value.__cause__)

