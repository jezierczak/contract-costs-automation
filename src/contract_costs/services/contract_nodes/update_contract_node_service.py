from dataclasses import replace

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.contract_nodes.dto.update_contract_node_command import UpdateContractNodeCommand
from contract_costs.services.contract_nodes.exceptions import ContractNodeCodeAlreadyExists
from contract_costs.unit_of_work import UnitOfWork


class UpdateContractNodeService(
    ActionHandler[UpdateContractNodeCommand, None]
):

    def execute(self, *, action:UpdateContractNodeCommand, uow:UnitOfWork):

        repo = uow.contract_nodes

        nodes = repo.list_by_contract(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )

        node = next(n for n in nodes if n.id == action.node_id)

        # UNIQUE CHECK (ważne)
        for n in nodes:
            if n.id != node.id and n.code == action.code:
                raise ContractNodeCodeAlreadyExists("Code must be unique, this contract node already exists")

        updated = replace(node,
            code=action.code,
            name=action.name,
            quantity=action.quantity,
            unit=action.unit,
            budget=action.planned_budget,
        )
        repo.update(updated)