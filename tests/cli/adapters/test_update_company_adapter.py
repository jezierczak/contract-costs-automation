from unittest.mock import MagicMock
from uuid import uuid4

from contract_costs.cli.adapters.company_adapter import update_company_from_cli
from contract_costs.model.company import Company, CompanyType
from contract_costs.model.company import Address


def test_update_company_from_cli_updates_company():
    company = Company(
        id=uuid4(),
        name="Company A",
        description=None,
        tax_number="123",
        address=Address("Street", "City", "00-000", "PL"),
        bank_account=None,
        role=CompanyType.CLIENT,
        tags=set(),
        is_active=True,
    )

    data = {
        "name": "Company A",
        "description": None,
        "address_street": "Street",
        "address_city": "City",
        "address_zip_code": "00-000",
        "address_country": "PL",
        "bank_account_number": None,
        "bank_account_country_code": None,
        "role": CompanyType.OWN,
    }

    update_service = MagicMock()

    update_company_from_cli(
        company=company,
        data=data,
        update_company_service=update_service,
    )

    update_service.execute.assert_called_once()

