from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractStatus
from contract_costs.services.contracts.apply.apply_contract_progress_excel_service import (
    ApplyContractProgressExcelService,
)
from contract_costs.services.contracts.apply.apply_contract_progress_service import (
    ApplyContractProgressService,
)
from contract_costs.services.contracts.apply.command.apply_contract_progress_excel_command import (
    ApplyContractProgressExcelCommand,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.helpers.contracts_helpers import make_contract_node


def make_contract(organization_id):
    return (
        ContractBuilder()
        .with_organization_id(organization_id)
        .with_owner(CompanyBuilder().with_role(CompanyType.OWN).build())
        .with_status(ContractStatus.ACTIVE)
        .build()
    )


def test_apply_progress_success(monkeypatch, contract_repo, contract_node_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()

    contract = make_contract(organization_id)
    contract_repo.add(contract)

    node = make_contract_node(
        organization_id=organization_id,
        contract_id=contract.id,
    )
    contract_node_repo.add_all([node])

    service = ApplyContractProgressExcelService(
        apply_contract_progress_service=ApplyContractProgressService(id_generator=uuid4)
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

    service.execute(
        action=ApplyContractProgressExcelCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            contract_id=contract.id,
            excel_path=Path("fake.xlsx"),
        ),
        uow=uow,
    )

    updated_nodes = contract_node_repo.list_by_contract(
        organization_id=organization_id,
        contract_id=contract.id,
    )
    updated_node = next(n for n in updated_nodes if n.id == node.id)
    assert updated_node.progress == Decimal("0.5")


def test_progress_rejects_non_leaf(monkeypatch, contract_repo, contract_node_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    contract = make_contract(organization_id)
    contract_repo.add(contract)

    parent = make_contract_node(organization_id=organization_id, contract_id=contract.id)
    child = make_contract_node(
        organization_id=organization_id,
        contract_id=contract.id,
        parent_id=parent.id,
    )
    contract_node_repo.add_all([parent, child])

    service = ApplyContractProgressExcelService(
        apply_contract_progress_service=ApplyContractProgressService(id_generator=uuid4)
    )

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
        service.execute(
            action=ApplyContractProgressExcelCommand(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                contract_id=contract.id,
                excel_path=Path("fake.xlsx"),
            ),
            uow=uow,
        )


def test_progress_rejects_invalid_range(monkeypatch, uow):
    service = ApplyContractProgressExcelService(
        apply_contract_progress_service=ApplyContractProgressService(id_generator=uuid4)
    )

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: [{
            "Contract": "ANY",
            "Node ID": str(uuid4()),
            "New Progress [%]": Decimal("150"),
            "Code": "A",
        }],
    )

    with pytest.raises(ValueError):
        service.execute(
            action=ApplyContractProgressExcelCommand(
                organization_id=uuid4(),
                actor_user_id=uuid4(),
                contract_id=uuid4(),
                excel_path=Path("fake.xlsx"),
            ),
            uow=uow,
        )


def test_progress_ignores_contract_column(monkeypatch, contract_repo, contract_node_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()

    contract = make_contract(organization_id)
    contract_repo.add(contract)

    node = make_contract_node(organization_id=organization_id, contract_id=contract.id)
    contract_node_repo.add_all([node])

    service = ApplyContractProgressExcelService(
        apply_contract_progress_service=ApplyContractProgressService(id_generator=uuid4)
    )

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: [{
            "Contract": "WRONG",
            "Node ID": str(node.id),
            "New Progress [%]": Decimal("50"),
            "Code": "A",
        }],
    )

    service.execute(
        action=ApplyContractProgressExcelCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            contract_id=contract.id,
            excel_path=Path("fake.xlsx"),
        ),
        uow=uow,
    )

    updated = contract_node_repo.get(
        organization_id=organization_id,
        contract_node_id=node.id,
    )
    assert updated is not None
    assert updated.progress == Decimal("0.5")


def test_progress_on_inactive_node_raises(monkeypatch, contract_repo, contract_node_repo, uow):
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

    service = ApplyContractProgressExcelService(
        apply_contract_progress_service=ApplyContractProgressService(id_generator=uuid4)
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
        service.execute(
            action=ApplyContractProgressExcelCommand(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                contract_id=contract.id,
                excel_path=Path("fake.xlsx"),
            ),
            uow=uow,
        )
