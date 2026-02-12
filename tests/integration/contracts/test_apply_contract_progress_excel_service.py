import pytest
from decimal import Decimal
from uuid import uuid4
from pathlib import Path
from unittest.mock import MagicMock

from contract_costs.model.contract import ContractStatus
from contract_costs.model.contract_node_progress import ContractNodeProgress
from contract_costs.model.company import CompanyType
from contract_costs.services.contracts.apply.apply_contract_progress_excel_service import (
    ApplyContractProgressExcelService,
)
from contract_costs.services.contracts.apply.apply_contract_progress_service import ApplyContractProgressService

from tests.builders.contract_builder import ContractBuilder
from tests.builders.company_builder import CompanyBuilder
from tests.helpers.contracts_helpers import make_contract_node


# =====================================================
# HELPERS
# =====================================================

def make_contract(organization_id):
    return (
        ContractBuilder()
        .with_organization_id(organization_id)
        .with_owner(CompanyBuilder().with_role(CompanyType.OWN).build())
        .with_status(ContractStatus.ACTIVE)
        .build()
    )





# =====================================================
# TESTS
# =====================================================

def test_apply_progress_success(
    monkeypatch,
    contract_repo,
    contract_node_repo,
):
    organization_id = uuid4()
    actor_user_id = uuid4()

    # --- create contract ---
    contract = make_contract(organization_id)
    contract_repo.add(contract)

    # --- create node ---
    node = make_contract_node(
        organization_id=organization_id,
        contract_id=contract.id,
    )
    contract_node_repo.add_all([node])

    # --- build services ---
    apply_progress_service = ApplyContractProgressService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        id_generator=uuid4,
    )

    excel_service = ApplyContractProgressExcelService(
        apply_contract_progress_service=apply_progress_service
    )

    # --- mock excel ---
    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: [{
            "Contract": contract.code,
            "Node ID": str(node.id),
            "New Progress [%]": Decimal("50"),
            "Code": node.code,
        }],
    )

    # --- execute ---
    excel_service.apply(
        contract=contract,
        excel_path=Path("fake.xlsx"),
        organization_id=organization_id,
        actor_user_id=actor_user_id,
    )

    # --- assert ---
    updated_nodes = contract_node_repo.list_by_contract(
        organization_id=organization_id,
        contract_id=contract.id,
    )

    updated_node = next(n for n in updated_nodes if n.id == node.id)

    assert updated_node.progress == Decimal("0.5")



def test_progress_rejects_non_leaf(monkeypatch):
    organization_id = uuid4()
    actor_user_id = uuid4()

    repo = MagicMock()
    repo2 = MagicMock()
    service = ApplyContractProgressExcelService(
        apply_contract_progress_service=ApplyContractProgressService(
            contract_repository=repo, contract_node_repository=repo2))

    contract = make_contract(organization_id)

    parent = make_contract_node(organization_id=organization_id, contract_id=contract.id)
    child = make_contract_node(organization_id=organization_id, contract_id=contract.id, parent_id=parent.id)

    repo.list_by_contract.return_value = [parent, child]

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: [{
            "Contract": contract.code,
            "Node ID": str(parent.id),
            "New Progress [%]": Decimal("50"),
            "Code": "A",
        }],
    )

    with pytest.raises(ValueError):
        service.apply(
            contract=contract,
            excel_path=Path("fake.xlsx"),
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        )


def test_progress_rejects_invalid_range(monkeypatch):
    organization_id = uuid4()
    actor_user_id = uuid4()

    repo = MagicMock()
    repo2 = MagicMock()
    service = ApplyContractProgressExcelService(
        apply_contract_progress_service=ApplyContractProgressService(
            contract_repository=repo, contract_node_repository=repo2))

    contract = make_contract(organization_id)
    node = make_contract_node(organization_id=organization_id, contract_id=contract.id)

    repo.list_by_contract.return_value = [node]

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: [{
            "Contract": contract.code,
            "Node ID": str(node.id),
            "New Progress [%]": Decimal("150"),
            "Code": "A",
        }],
    )

    with pytest.raises(ValueError):
        service.apply(
            contract=contract,
            excel_path=Path("fake.xlsx"),
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        )


def test_progress_rejects_wrong_contract(monkeypatch):
    organization_id = uuid4()
    actor_user_id = uuid4()

    repo = MagicMock()
    repo2 = MagicMock()
    service = ApplyContractProgressExcelService(
        apply_contract_progress_service=ApplyContractProgressService(
            contract_repository=repo, contract_node_repository=repo2))

    contract = make_contract(organization_id)
    node = make_contract_node(organization_id=organization_id, contract_id=contract.id)

    repo.list_by_contract.return_value = [node]

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: [{
            "Contract": "WRONG",
            "Node ID": str(node.id),
            "New Progress [%]": Decimal("50"),
            "Code": "A",
        }],
    )

    with pytest.raises(ValueError):
        service.apply(
            contract=contract,
            excel_path=Path("fake.xlsx"),
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        )


def test_progress_on_inactive_node_raises(
    monkeypatch,
    contract_repo,
    contract_node_repo,
):
    organization_id = uuid4()
    actor_user_id = uuid4()

    contract = make_contract(organization_id)
    contract_repo.add(contract)

    node = make_contract_node(
        organization_id=organization_id,
        contract_id=contract.id,
        is_active=False,
    )
    contract_node_repo.add_all([node])

    apply_progress_service = ApplyContractProgressService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        id_generator=uuid4,
    )

    excel_service = ApplyContractProgressExcelService(
        apply_contract_progress_service=apply_progress_service
    )

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: [{
            "Contract": contract.code,
            "Node ID": str(node.id),
            "New Progress [%]": Decimal("50"),
            "Code": node.code,
        }],
    )

    with pytest.raises(ValueError, match="inactive"):
        excel_service.apply(
            contract=contract,
            excel_path=Path("fake.xlsx"),
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        )
