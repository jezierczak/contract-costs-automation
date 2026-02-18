from pathlib import Path

import pytest
from decimal import Decimal
from datetime import date
from uuid import uuid4

from contract_costs.common.time import utc_now
from contract_costs.model.contract_node_progress import ContractNodeProgress
from contract_costs.services.contracts.apply.apply_contract_progress_excel_service import \
    ApplyContractProgressExcelService
from contract_costs.services.contracts.apply.apply_contract_progress_service import (
    ApplyContractProgressService,
)
from contract_costs.services.contracts.apply.command.apply_contract_progerss_command import (
    ApplyContractProgressCommand,
    ContractNodeProgressUpdate,
)
from contract_costs.services.contracts.apply.command.apply_contract_progress_excel_command import (
    ApplyContractProgressExcelCommand,
)
from contract_costs.model.contract import ContractStatus
from contract_costs.model.company import CompanyType
from tests.builders.contract_builder import ContractBuilder
from tests.builders.company_builder import CompanyBuilder
from tests.helpers.contracts_helpers import make_contract_node
from tests.integration.contracts.test_apply_contract_progress_excel_service import make_contract


# ============================================================
# HELPERS
# ============================================================

def make_command(
    *,
    organization_id,
    actor_user_id,
    contract_id,
    updates,
):
    return ApplyContractProgressCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        contract_id=contract_id,
        updates=updates,
    )


# ============================================================
# TESTS
# ============================================================

def test_contract_not_found_raises(uow):
    service = ApplyContractProgressService(
        id_generator=uuid4,
    )

    cmd = make_command(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        contract_id=uuid4(),
        updates=[],
    )

    with pytest.raises(ValueError, match="Contract does not exist"):
        service.execute(action=cmd, uow=uow)


def test_contract_has_no_nodes_raises(contract_repo, uow):
    organization_id = uuid4()
    contract_id = uuid4()

    contract = (
        ContractBuilder()
        .with_id(contract_id)
        .with_organization_id(organization_id)
        .with_owner(
            CompanyBuilder().with_role(CompanyType.OWN).build()
        )
        .with_status(ContractStatus.ACTIVE)
        .build()
    )
    contract_repo.add(contract)

    service = ApplyContractProgressService(
        id_generator=uuid4,
    )

    cmd = make_command(
        organization_id=organization_id,
        actor_user_id=uuid4(),
        contract_id=contract_id,
        updates=[],
    )

    with pytest.raises(ValueError, match="Contract has no nodes"):
        service.execute(action=cmd, uow=uow)


def test_node_not_found_raises(contract_repo, contract_node_repo, uow):
    organization_id = uuid4()
    contract_id = uuid4()

    contract = (
        ContractBuilder()
        .with_id(contract_id)
        .with_organization_id(organization_id)
        .with_owner(
            CompanyBuilder().with_role(CompanyType.OWN).build()
        )
        .with_status(ContractStatus.ACTIVE)
        .build()
    )
    contract_repo.add(contract)

    service = ApplyContractProgressService(
        id_generator=uuid4,
    )
    node = make_contract_node(
        organization_id=organization_id,
        contract_id=contract_id,
    )

    contract_node_repo.add_all([node])

    update = ContractNodeProgressUpdate(
        contract_node_id=uuid4(),
        progress=Decimal("0.5"),
        progress_date=date.today(),
    )

    cmd = make_command(
        organization_id=organization_id,
        actor_user_id=uuid4(),
        contract_id=contract_id,
        updates=[update],
    )

    with pytest.raises(ValueError, match="not found"):
        service.execute(action=cmd, uow=uow)


def test_cannot_set_progress_on_non_leaf(contract_repo, contract_node_repo, uow):
    organization_id = uuid4()
    contract_id = uuid4()

    contract = (
        ContractBuilder()
        .with_id(contract_id)
        .with_organization_id(organization_id)
        .with_owner(
            CompanyBuilder().with_role(CompanyType.OWN).build()
        )
        .with_status(ContractStatus.ACTIVE)
        .build()
    )
    contract_repo.add(contract)

    parent = make_contract_node(
        organization_id=organization_id,
        contract_id=contract_id,
        code="A",
    )

    child = make_contract_node(
        organization_id=organization_id,
        contract_id=contract_id,
        code="B",
        parent_id=parent.id,
    )

    contract_node_repo.add_all([parent, child])

    service = ApplyContractProgressService(
        id_generator=uuid4,
    )

    update = ContractNodeProgressUpdate(
        contract_node_id=parent.id,
        progress=Decimal("0.5"),
        progress_date=date.today(),
    )

    cmd = make_command(
        organization_id=organization_id,
        actor_user_id=uuid4(),
        contract_id=contract_id,
        updates=[update],
    )

    with pytest.raises(ValueError, match="leaf"):
        service.execute(action=cmd, uow=uow)


def test_cannot_decrease_progress(contract_repo, contract_node_repo, uow):
    organization_id = uuid4()
    contract_id = uuid4()

    contract = (
        ContractBuilder()
        .with_id(contract_id)
        .with_organization_id(organization_id)
        .with_owner(
            CompanyBuilder().with_role(CompanyType.OWN).build()
        )
        .with_status(ContractStatus.ACTIVE)
        .build()
    )
    contract_repo.add(contract)

    node = make_contract_node(
        organization_id=organization_id,
        contract_id=contract_id,
        code="A",
    )

    contract_node_repo.add_all([node])

    # first progress
    contract_node_repo.add_progress(
        ContractNodeProgress(
            id=uuid4(),
            organization_id=organization_id,
            contract_node_id=node.id,
            progress=Decimal("0.6"),
            progress_date=date.today(),
            created_at=utc_now(),
            created_by_user_id=None,
            updated_at=None,
            updated_by_user_id=None,
        )
    )

    service = ApplyContractProgressService(
        id_generator=uuid4,
    )

    update = ContractNodeProgressUpdate(
        contract_node_id=node.id,
        progress=Decimal("0.4"),
        progress_date=date.today(),
    )

    cmd = make_command(
        organization_id=organization_id,
        actor_user_id=uuid4(),
        contract_id=contract_id,
        updates=[update],
    )

    with pytest.raises(ValueError, match="cannot decrease"):
        service.execute(action=cmd, uow=uow)


def test_valid_progress_is_saved(contract_repo, contract_node_repo, uow):
    organization_id = uuid4()
    contract_id = uuid4()

    contract = (
        ContractBuilder()
        .with_id(contract_id)
        .with_organization_id(organization_id)
        .with_owner(
            CompanyBuilder().with_role(CompanyType.OWN).build()
        )
        .with_status(ContractStatus.ACTIVE)
        .build()
    )
    contract_repo.add(contract)

    node = make_contract_node(
        organization_id=organization_id,
        contract_id=contract_id,
        code="A",
    )

    contract_node_repo.add_all([node])

    service = ApplyContractProgressService(
        id_generator=uuid4,
    )

    update = ContractNodeProgressUpdate(
        contract_node_id=node.id,
        progress=Decimal("0.5"),
        progress_date=date.today(),
    )

    cmd = make_command(
        organization_id=organization_id,
        actor_user_id=uuid4(),
        contract_id=contract_id,
        updates=[update],
    )

    service.execute(action=cmd, uow=uow)

    nodes = contract_node_repo.list_by_contract(
        organization_id=organization_id,
        contract_id=contract_id,
    )

    assert nodes[0].progress == Decimal("0.5")

def test_apply_progress_success(
    monkeypatch,
    contract_repo,
    contract_node_repo,
    uow,
):
    organization_id = uuid4()
    actor_user_id = uuid4()

    # --- create real contract ---
    contract = make_contract(organization_id)
    contract_repo.add(contract)

    # --- create real node (leaf) ---
    node = make_contract_node(
        organization_id=organization_id,
        contract_id=contract.id,
    )
    contract_node_repo.add_all([node])

    # --- build real service ---
    apply_progress_service = ApplyContractProgressService(
        id_generator=uuid4,
    )

    service = ApplyContractProgressExcelService(
        apply_contract_progress_service=apply_progress_service
    )

    # --- mock Excel ---
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
    service.execute(
        action=ApplyContractProgressExcelCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            contract_id=contract.id,
            excel_path=Path("fake.xlsx"),
        ),
        uow=uow,
    )

    # --- assert progress persisted ---
    updated_nodes = contract_node_repo.list_by_contract(
        organization_id=organization_id,
        contract_id=contract.id,
    )

    updated_node = next(n for n in updated_nodes if n.id == node.id)

    assert updated_node.progress is not None
    assert updated_node.progress == Decimal("0.5")
