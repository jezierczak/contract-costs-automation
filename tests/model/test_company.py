import logging

import pytest

from contract_costs.model.company import BankAccount, Address


class TestBankAccount:

    def test_bank_account_pl_valid(self) -> None:
        acc = BankAccount("91221122112211221122221111", "PL")
        assert acc.iban == "PL91221122112211221122221111"

    def test_bank_account_invalid_length_logs_warning(self,caplog):
        with caplog.at_level(logging.WARNING):
            BankAccount(number="123", country_code="PL")

        assert "Polish account number must have 26 digits" in caplog.text


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

    def test_address_invalid_zip_code_logs_warning(self,caplog):
        with caplog.at_level(logging.WARNING):
            Address(
                street="x",
                city="y",
                zip_code="12345",
                country="PL",
            )

        assert "Invalid zip code" in caplog.text

    def test_address_poland_case_insensitive(self) -> None:
        Address(
            street="Street",
            zip_code="12-345",
            city="City",
            country="polska",
        )




