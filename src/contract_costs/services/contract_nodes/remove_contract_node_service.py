from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.contract_nodes.dto.remove_contract_node_command import RemoveContractNodeCommand

from contract_costs.unit_of_work import UnitOfWork


class RemoveContractNodeService(
    ActionHandler[RemoveContractNodeCommand, None]
):

    def execute(
        self,
        *,
        action: RemoveContractNodeCommand,
        uow: UnitOfWork,
    ) -> None:

        node_repo = uow.contract_nodes

        # --------------------------------------------
        # BLOCK REMOVE IF VALUES EXIST
        # --------------------------------------------
        if node_repo.node_has_values(
            contract_node_id=action.node_id,
            organization_id=action.organization_id,
        ):
            raise ValueError(
                "Cannot remove contract node with values"
            )

        # --------------------------------------------
        # DELETE
        # --------------------------------------------
        node_repo.delete_many(
            ids=[action.node_id],
            organization_id=action.organization_id,
        )