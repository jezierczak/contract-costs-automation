from unittest.mock import MagicMock

from contract_costs.cli.adapters.company_adapter import create_company_from_cli
from contract_costs.model.company import Address
from contract_costs.model.company import BankAccount
from contract_costs.model.company import CompanyType


def test_create_company_from_cli_with_bank_account():
    # --- given ---
    data = {
        "name": "Company A",
        "tax_number": "1234567890",
        "description": "Test company",
        "address_street": "Main Street 1",
        "address_city": "Krakow",
        "address_zip_code": "30-001",
        "address_country": "PL",
        "bank_account_number": "12345678901234567890123456",
        "bank_account_country_code": "PL",
        "role": CompanyType.OWN,

    }

    create_company_service = MagicMock()

    # --- when ---
    create_company_from_cli(
        data=data,
        create_company_service=create_company_service,
    )

    # --- then ---
    create_company_service.execute.assert_called_once()

    kwargs = create_company_service.execute.call_args.kwargs

    assert kwargs["name"] == "Company A"
    assert kwargs["tax_number"] == "1234567890"
    assert kwargs["description"] == "Test company"
    assert kwargs["role"] == CompanyType.OWN



    assert isinstance(kwargs["address"], Address)
    assert kwargs["address"].street == "Main Street 1"
    assert kwargs["address"].city == "Krakow"
    assert kwargs["address"].zip_code == "30-001"
    assert kwargs["address"].country == "PL"

    assert isinstance(kwargs["bank_account"], BankAccount)
    assert kwargs["bank_account"].number == "12345678901234567890123456"
    assert kwargs["bank_account"].country_code == "PL"

def test_create_company_from_cli_without_bank_account():
    # --- given ---
    data = {
        "name": "Company B",
        "tax_number": "0987654321",
        "description": None,
        "address_street": "Second Street 5",
        "address_city": "Warsaw",
        "address_zip_code": "00-001",
        "address_country": "PL",
        "bank_account_number": None,
        "bank_account_country_code": None,
        "role": CompanyType.CLIENT,
    }

    create_company_service = MagicMock()

    # --- when ---
    create_company_from_cli(
        data=data,
        create_company_service=create_company_service,
    )

    # --- then ---
    kwargs = create_company_service.execute.call_args.kwargs

    assert kwargs["bank_account"] is None

