from uuid import uuid4

import pytest
from unittest.mock import MagicMock


from contract_costs.model.company import CompanyType
from contract_costs.services.companies.apply.apply_companies_from_excel_service import ApplyCompaniesFromExcelService
from contract_costs.services.companies.apply.command import CompanyActionCommand, CompanyActionType


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
    return CompanyActionCommand(
        action=CompanyActionType.UPDATE,
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

def test_apply_create_calls_create(apply_service: MagicMock, base_command: CompanyActionCommand):
    base_command = base_command.__class__(**{
        **base_command.__dict__,
        "action": CompanyActionType.CREATE,
        "company_id": None,
    })

    apply_service.apply([base_command])

    apply_service._create.execute.assert_called_once()
    apply_service._update.execute.assert_not_called()


def test_apply_update_calls_update(apply_service: MagicMock, base_command: CompanyActionCommand):
    apply_service.apply([base_command])

    apply_service._update.execute.assert_called_once()
    apply_service._create.execute.assert_not_called()


def test_apply_activate_calls_activate(apply_service: MagicMock, base_command: CompanyActionCommand):
    cmd = base_command.__class__(**{
        **base_command.__dict__,
        "action": CompanyActionType.ACTIVATE,
    })

    apply_service.apply([cmd])

    apply_service._activate.execute.assert_called_once_with(cmd.company_id)


def test_apply_deactivate_calls_deactivate(apply_service: MagicMock, base_command: CompanyActionCommand):
    cmd = base_command.__class__(**{
        **base_command.__dict__,
        "action": CompanyActionType.DEACTIVATE,
    })

    apply_service.apply([cmd])

    apply_service._deactivate.execute.assert_called_once_with(cmd.company_id)


def test_apply_none_action_does_nothing(apply_service: MagicMock, base_command: CompanyActionCommand):
    cmd = base_command.__class__(**{
        **base_command.__dict__,
        "action": CompanyActionType.NONE,
    })

    apply_service.apply([cmd])

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
        apply_service.apply([cmd])

    # sprawdzamy przyczynę
    assert isinstance(exc_info.value.__cause__, ValueError)
    assert "UPDATE requires company_id" in str(exc_info.value.__cause__)

