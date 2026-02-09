from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime

from contract_costs.cli.adapters.company_adapter import update_company_from_cli
from contract_costs.model.company import Company, CompanyType, Contact, Address
from contract_costs.services.companies.dto.update_company_command import UpdateCompanyCommand


def test_update_company_from_cli_updates_company():
    org_id = uuid4()
    user_id = uuid4()
    now = datetime.now()

    company = Company(
        id=uuid4(),
        organization_id=org_id,

        name="Company A",
        description=None,
        tax_number="123",

        address=Address("Street", "City", "00-000", "PL"),
        contact=None,
        bank_account=None,

        role=CompanyType.CLIENT,
        tags=set(),
        is_active=True,

        created_at=now,
        created_by_user_id=user_id,
        updated_at=None,
        updated_by_user_id=None,
    )

    data = {
        "name": "Company A",
        "tax_number": "123",
        "description": None,
        "address_street": "Street",
        "address_city": "City",
        "address_zip_code": "00-000",
        "address_country": "PL",
        "phone_number": "123",
        "email": "email@email.com",
        "bank_account_number": None,
        "bank_account_country_code": None,
        "role": CompanyType.OWN,
    }

    update_service = MagicMock()

    update_company_from_cli(
        organization_id=org_id,
        actor_user_id=user_id,
        company=company,
        data=data,
        update_company_service=update_service,
    )

    # --- ASSERT ---
    update_service.execute.assert_called_once()

    cmd = update_service.execute.call_args.args[0]
    assert isinstance(cmd, UpdateCompanyCommand)

    assert cmd.organization_id == org_id
    assert cmd.actor_user_id == user_id
    assert cmd.company_id == company.id
    assert cmd.role == CompanyType.OWN
    assert cmd.address.city == "City"
    assert cmd.contact.email == "email@email.com"
