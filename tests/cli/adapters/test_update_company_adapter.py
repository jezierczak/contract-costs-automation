from unittest.mock import MagicMock
from uuid import uuid4

from contract_costs.cli.adapters.company_adapter import update_company_from_cli
from contract_costs.model.company import Company, CompanyType
from contract_costs.model.company import Address


def test_update_company_from_cli_changes_role():
    company = Company(
        id=uuid4(),
        name="Company A",
        description=None,
        tax_number="123",
        address=Address(
            street="Street",
            city="City",
            zip_code="00-000",
            country="PL",
        ),
        bank_account=None,
        role=CompanyType.CLIENT,
        tags=set(),
        is_active=True,
    )

    data = {
        "role": CompanyType.OWN,
    }

    change_role_service = MagicMock()

    update_company_from_cli(
        company=company,
        data=data,
        change_role_service=change_role_service,
    )

    change_role_service.execute.assert_called_once_with(
        company_id=company.id,
        new_role=CompanyType.OWN,
    )

def test_update_company_from_cli_does_not_call_service_if_role_same():
    company = Company(
        id=uuid4(),
        name="Company A",
        description=None,
        tax_number="123",
        address=Address(
            street="Street",
            city="City",
            zip_code="00-000",
            country="PL",
        ),
        bank_account=None,
        role=CompanyType.OWN,
        tags=set(),
        is_active=True,
    )

    data = {
        "role": CompanyType.OWN,
    }

    change_role_service = MagicMock()

    update_company_from_cli(
        company=company,
        data=data,
        change_role_service=change_role_service,
    )

    change_role_service.execute.assert_not_called()
