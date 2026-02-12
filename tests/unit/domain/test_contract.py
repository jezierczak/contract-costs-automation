from contract_costs.model.contract import ContractStatus, Contract
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from pathlib import Path

def test_contract_creation():
    contract = ContractBuilder().build()

    assert contract.code == "C-001"
    assert contract.status == ContractStatus.PLANNED
    assert contract.owner is not None

def test_contract_is_active_true_when_status_active():
    contract = ContractBuilder().with_status(ContractStatus.ACTIVE).build()

    assert contract.is_active is True

def test_contract_is_active_false_for_other_statuses():
    contract = ContractBuilder().with_status(ContractStatus.PLANNED).build()

    assert contract.is_active is False



def test_contract_path_generates_safe_path():
    owner = CompanyBuilder().build()

    path = Contract.contract_path(owner, "Big Project 2025")

    expected = Path(owner.name) / "big_project_2025"

    assert path == expected


def test_contract_status_can_be_modified():
    contract = ContractBuilder().build()

    contract.status = ContractStatus.ACTIVE

    assert contract.is_active is True

import pytest

def test_contract_disallows_dynamic_attributes():
    contract = ContractBuilder().build()

    with pytest.raises(AttributeError):
        contract.random_field = "boom"


def test_contract_path_handles_spaces_in_owner_name():
    owner = CompanyBuilder().build()
    owner.name = "My Company Sp. z o.o."

    path = Contract.contract_path(owner, "Test")

    assert " " in str(path)  # obecnie spacje zostają
