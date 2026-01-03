import builtins
from unittest.mock import MagicMock
from uuid import uuid4

from contract_costs.cli.commands.edit.edit_company import handle_edit_company
from contract_costs.model.company import CompanyType, Company, Address, Contact


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
        contact=Contact(
            phone_number="1515215",
            email="example@email.com"
        ),
        bank_account=None,
        role=CompanyType.CLIENT,
        tags=set(),
        is_active=True,
    )

    # input()
    inputs = iter(["123", "y"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # interactive prompt
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

    services = MagicMock()
    services.company_repository.get_by_tax_number.return_value = company

    monkeypatch.setattr(
        "contract_costs.cli.commands.edit_company.get_services",
        lambda: services,
    )

    # MOCKUJEMY ADAPTER
    adapter = MagicMock()
    monkeypatch.setattr(
        "contract_costs.cli.commands.edit_company.update_company_from_cli",
        adapter,
    )

    handle_edit_company()

    adapter.assert_called_once()
