
from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.contract_node import ContractNode
from contract_costs.services.contract_nodes.dto.add_contract_node_command import AddContractNodeCommand
from contract_costs.services.contract_nodes.exceptions import ContractNodeCodeAlreadyExists
from contract_costs.unit_of_work import UnitOfWork


class AddContractNodeService(
    ActionHandler[AddContractNodeCommand, None]
):

    def __init__(self, clock=utc_now, gen = new_uuid):
        self._clock = clock
        self._gen_number=gen

    def execute(self, *, action:AddContractNodeCommand, uow:UnitOfWork):

        node_repo = uow.contract_nodes

        nodes = node_repo.list_by_contract(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )

        root = next(
            (n for n in nodes if n.parent_id is None),
            None
        )

        if root is None:
            root = ContractNode(
                id=self._gen_number(),
                contract_id=action.contract_id,
                parent_id=None,
                code="ROOT",
                name="ROOT",
                budget=None,
                quantity=None,
                unit=None,
                is_active=True,
                progress_history={},
                organization_id=action.organization_id,
                created_by_user_id=action.actor_user_id,
                updated_by_user_id=action.actor_user_id,
                created_at=self._clock(),
                updated_at=None,
            )
            node_repo.add(root)

        parent_id = action.parent_id or root.id

        existing_codes = {n.code for n in nodes}

        if action.code and action.code in existing_codes:
            raise ContractNodeCodeAlreadyExists(action.code)

        new_node = ContractNode(
            id=self._gen_number(),
            contract_id=action.contract_id,
            parent_id=parent_id,
            name=action.name,
            code=action.code if action.code else self._next_code(nodes),  # temporary
            budget=action.planned_budget,
            quantity=action.quantity,
            unit=action.unit,
            is_active=True,
            progress_history={},
            organization_id=action.organization_id,
            created_by_user_id=action.actor_user_id,
            updated_by_user_id=action.actor_user_id,
            created_at=self._clock(),
            updated_at=None,
        )

        node_repo.add(new_node)

    @staticmethod
    def _next_code(existing_nodes):
        i = 1
        existing_codes = {n.code for n in existing_nodes}

        while True:
            code = f"NODE-{i:03}"
            if code not in existing_codes:
                return code
            i += 1