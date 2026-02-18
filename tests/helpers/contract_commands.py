from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractStatus, ContractType
from contract_costs.model.contract_node import ContractNodeInput
from contract_costs.services.contracts.apply.command.update_contract_structure_command import \
    UpdateContractStructureCommand
from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand
from tests.builders.company_builder import CompanyBuilder
from tests.helpers.contracts_helpers import make_node_input


def make_contract_command(contract_node_input: list[ContractNodeInput]):
    return CreateContractCommand(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        code="C-1",
        name="Test Contract",
        description=None,
        owner=CompanyBuilder().with_role(CompanyType.OWN).build(),   # możesz podać mock Company jeśli potrzebne
        client=None,
        start_date=None,
        end_date=None,
        budget=Decimal("1000"),
        path=None,
        status=ContractStatus.ACTIVE,
        contract_type=ContractType.PROJECT,
        contract_node_input=contract_node_input,
    )




def make_update_structure_command(
    *,
    organization_id=None,
    actor_user_id=None,
    contract_id=None,
    contract_node_input=None,
) -> UpdateContractStructureCommand:

    return UpdateContractStructureCommand(
        organization_id=organization_id or uuid4(),
        actor_user_id=actor_user_id or uuid4(),
        contract_id=contract_id or uuid4(),

        name="Updated Contract",
        description="Updated description",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        budget=Decimal("1000"),
        status=ContractStatus.ACTIVE,
        path=Path("/tmp/test"),

        contract_node_input=contract_node_input
        or [
            make_node_input(code="A"),
        ],
    )