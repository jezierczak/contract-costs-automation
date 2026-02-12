from pathlib import Path
from datetime import date, datetime
from uuid import uuid4
from decimal import Decimal

from contract_costs.model.contract import Contract, ContractStatus
from contract_costs.services.contracts.prepare.mappers.contract_prepare_mapper import (
    ContractPrepareMapper,
)
from tests.builders.company_builder import CompanyBuilder


# =========================================
# HELPERS
# =========================================




def make_contract(
    *,
    client=True,
    path=True,
):
    return Contract(
        id=uuid4(),
        organization_id=uuid4(),
        code="C-100",
        name="Test Contract",
        description="Desc",
        owner=CompanyBuilder().with_tax_number("1111111111").build(),
        client=CompanyBuilder().with_tax_number("2222222222").build() if client else None,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        budget=Decimal("1000"),
        path=Path("/tmp/test.xlsx") if path else None,
        status=ContractStatus.ACTIVE,
        created_at=datetime.now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
    )


# =========================================
# TESTS
# =========================================

def test_maps_all_fields_correctly():
    contract = make_contract()

    dto = ContractPrepareMapper.map(contract)

    assert dto.code == "C-100"
    assert dto.name == "Test Contract"
    assert dto.owner_nip == "1111111111"
    assert dto.client_nip == "2222222222"
    assert dto.description == "Desc"
    assert dto.start_date == date(2024, 1, 1)
    assert dto.end_date == date(2024, 12, 31)
    assert dto.budget == Decimal("1000")
    assert Path(dto.path).name == "test.xlsx"
    assert dto.status == ContractStatus.ACTIVE.name


def test_client_none_is_mapped_as_none():
    contract = make_contract(client=False)

    dto = ContractPrepareMapper.map(contract)

    assert dto.client_nip is None


def test_path_none_is_stringified_correctly():
    contract = make_contract(path=False)

    dto = ContractPrepareMapper.map(contract)

    # str(None) == "None"
    # jeśli chcesz inne zachowanie – to tu wyjdzie
    assert dto.path == "None"
