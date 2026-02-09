from unittest.mock import MagicMock
from uuid import uuid4

from contract_costs.cli.adapters.company_adapter import create_company_from_cli
from contract_costs.model.company import Address
from contract_costs.model.company import BankAccount
from contract_costs.model.company import CompanyType
from contract_costs.services.companies.dto.create_company_command import CreateCompanyCommand

org_id = uuid4()
user_id = uuid4()

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
        "phone_number": "0987654321",
        "email": "email@example.com",
        "bank_account_number": "12345678901234567890123456",
        "bank_account_country_code": "PL",
        "role": CompanyType.OWN,
    }

    create_company_service = MagicMock()

    # --- when ---
    create_company_from_cli(
        organization_id=org_id,
        actor_user_id=user_id,
        data=data,
        create_company_service=create_company_service,
    )

    # --- then ---
    create_company_service.execute.assert_called_once()

    cmd = create_company_service.execute.call_args.args[0]
    assert isinstance(cmd, CreateCompanyCommand)

    # --- core fields ---
    assert cmd.organization_id == org_id
    assert cmd.actor_user_id == user_id
    assert cmd.name == "Company A"
    assert cmd.tax_number == "1234567890"
    assert cmd.description == "Test company"
    assert cmd.role == CompanyType.OWN

    # --- address ---
    assert isinstance(cmd.address, Address)
    assert cmd.address.street == "Main Street 1"
    assert cmd.address.city == "Krakow"
    assert cmd.address.zip_code == "30-001"
    assert cmd.address.country == "PL"

    # --- bank account ---
    assert isinstance(cmd.bank_account, BankAccount)
    assert cmd.bank_account.account_number == "12345678901234567890123456"
    assert cmd.bank_account.country_code == "PL"

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
        "phone_number": "0987654321",
        "email": "email@example.com",
        "bank_account_number": None,
        "bank_account_country_code": None,
        "role": CompanyType.CLIENT,
    }

    create_company_service = MagicMock()

    # --- when ---
    create_company_from_cli(
        organization_id=org_id,
        actor_user_id=user_id,
        data=data,
        create_company_service=create_company_service,
    )

    # --- then ---
    create_company_service.execute.assert_called_once()

    cmd = create_company_service.execute.call_args.args[0]
    assert isinstance(cmd, CreateCompanyCommand)

    assert cmd.organization_id == org_id
    assert cmd.actor_user_id == user_id
    assert cmd.bank_account is None   # 🔥 TO JEST KLUCZOWE

