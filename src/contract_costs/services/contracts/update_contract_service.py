from dataclasses import replace

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.contracts.dto.update_contract_command import (
    UpdateContractCommand,
)


class UpdateContractService(
    ActionHandler[UpdateContractCommand, None]
):

    def execute(self, *, action: UpdateContractCommand, uow):

        repo = uow.contracts

        contract = repo.get(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )

        if not contract:
            raise ValueError("Contract not found")

        # ---- UNIQUE CODE CHECK ----
        all_contracts = repo.list_contracts(
            organization_id=action.organization_id
        )

        for c in all_contracts:
            if c.id != contract.id and c.code == action.code:
                raise ValueError("Kod kontraktu już istnieje")

        updated = replace(
            contract,
            code=action.code,
            name=action.name,
            description=action.description,
            owner=action.owner,
            client=action.client,
            updated_by_user_id=action.actor_user_id,
        )

        repo.update(updated)