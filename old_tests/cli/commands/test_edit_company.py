import builtins
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime

from contract_costs.cli.commands.edit.edit_company import handle_edit_company
from contract_costs.model.company import CompanyType, Company, Address, Contact


def test_handle_edit_company_happy_path(monkeypatch):
    company_id = uuid4()
    org_id = uuid4()
    user_id = uuid4()
    now = datetime.now()

    company = Company(
        id=company_id,
        organization_id=org_id,

        name="Company A",
        description=None,
        tax_number="123",

        address=Address(
            street="Street",
            city="City",
            zip_code="00-000",
            country="PL",
        ),
        contact=Contact(
            phone_number="1515215",
            email="example@email.com",
        ),
        bank_account=None,

        role=CompanyType.CLIENT,
        tags=set(),
        is_active=True,

        created_at=now,
        created_by_user_id=user_id,
        updated_at=None,
        updated_by_user_id=None,
    )

    # --- input() ---
    inputs = iter(["123", "y"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # --- interactive prompt ---
    monkeypatch.setattr(
        "contract_costs.cli.commands.edit.edit_company.interactive_prompt",
        lambda _: {
            "name": "Updated",
            "description": "Desc",
            "address_street": "New",
            "address_city": "City",
            "address_zip_code": "00-000",
            "address_country": "PL",
            "phone_number": "1515215",
            "email": "example@email.com",
            "bank_account_number": None,
            "bank_account_country_code": None,
            "role": CompanyType.OWN,
            "is_active": False,
        },
    )

    # --- services + context ---
    services = MagicMock()
    services.context.current_organization_id.return_value = org_id
    services.context.current_user_id.return_value = user_id

    services.company_repository.get_by_tax_number.return_value = company

    monkeypatch.setattr(
        "contract_costs.cli.commands.edit.edit_company.get_services",
        lambda: services,
    )

    # --- adapter ---
    adapter = MagicMock()
    monkeypatch.setattr(
        "contract_costs.cli.commands.edit.edit_company.update_company_from_cli",
        adapter,
    )

    # --- run ---
    handle_edit_company(args=None)

    # --- assert ---
    adapter.assert_called_once()
