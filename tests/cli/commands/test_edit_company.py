from unittest.mock import MagicMock
from uuid import uuid4

import builtins

from contract_costs.cli.commands.edit_company import handle_edit_company
from contract_costs.model.company import Company, CompanyType
from contract_costs.model.company import Address


def test_handle_edit_company_happy_path(monkeypatch):
    company_id = uuid4()

    company = Company(
        id=company_id,
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

    # --- mock input ---
    inputs = iter(["123", "y"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # --- mock interactive_prompt ---
    monkeypatch.setattr(
        "contract_costs.cli.commands.edit_company.interactive_prompt",
        lambda _: {
            "name": "Updated",
            "description": "Desc",
            "address_street": "New",
            "address_city": "City",
            "address_zip_code": "00-000",
            "address_country": "PL",
            "bank_account_number": None,
            "bank_account_country_code": None,
            "role": CompanyType.OWN,
            "is_active": False,
        },
    )

    # --- mock services ---
    services = MagicMock()
    services.company_repository.get_by_tax_number.return_value = company
    services.change_company_role = MagicMock()

    monkeypatch.setattr(
        "contract_costs.cli.commands.edit_company.get_services",
        lambda: services,
    )

    # --- execute ---
    handle_edit_company()

    services.change_company_role.execute.assert_called_once_with(
        company_id=company.id,
        new_role=CompanyType.OWN,
    )
