import pytest

from contract_costs.model.company import BankAccount, Address


class TestBankAccount:

    def test_bank_account_pl_valid(self) -> None:
        acc = BankAccount("91221122112211221122221111", "PL")
        assert acc.iban == "PL91221122112211221122221111"


    def test_bank_account_invalid_length(self) -> None:
        with pytest.raises(ValueError):
            BankAccount("123", "PL")


class TestAddress:

    def test_address_valid_no_poland(self) -> None:
        add = Address(street="Street",zip_code="34-7000",city="City",country="Country")
        assert add.street == "Street"
        assert add.zip_code == "34-7000"
        assert add.city == "City"
        assert add.country == "Country"

    def test_address_valid_poland(self) -> None:
        add = Address(street="Street",zip_code="34-700",city="City",country="PL")
        assert add.street == "Street"
        assert add.zip_code == "34-700"
        assert add.city == "City"
        assert add.country == "PL"

    def test_address_invalid_zip_code_country(self) -> None:
        with pytest.raises(ValueError, match="Invalid zip code"):
            Address(
                street="Street",
                zip_code="34-7aa",
                city="City",
                country="Polska",
            )

    def test_address_poland_case_insensitive(self) -> None:
        Address(
            street="Street",
            zip_code="12-345",
            city="City",
            country="polska",
        )




