from decimal import Decimal
from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.contract_node_progress import ContractNodeProgress
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.services.contracts.apply.command.apply_contract_progerss_command import (
    ApplyContractProgressCommand,
    ContractNodeProgressUpdate,
)
from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex
from contract_costs.unit_of_work import UnitOfWork


class ApplyContractProgressService(ActionHandler[ApplyContractProgressCommand, None]):

    def __init__(
        self,
        # contract_repository: ContractRepository,
        # contract_node_repository: ContractNodeRepository,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        # self._contract_repo = contract_repository
        # self._node_repo = contract_node_repository
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, *, action: ApplyContractProgressCommand, uow: UnitOfWork) -> None:
        contract_repo = uow.contracts
        node_repo = uow.contract_nodes

        contract = self._get_contract(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
            contract_repo=contract_repo
        )

        nodes = node_repo.list_by_contract(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )

        if not nodes:
            raise ValueError("Contract has no nodes")

        tree = ContractNodeTreeIndex(nodes)
        nodes_by_id = {n.id: n for n in nodes}

        for update in action.updates:
            self._apply_single_update(
                node_repo=node_repo,
                contract=contract,
                update=update,
                nodes_by_id=nodes_by_id,
                tree=tree,
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
            )

    def _apply_single_update(
        self,
        *,
        node_repo: ContractNodeRepository,
        contract: Contract,
        update: ContractNodeProgressUpdate,
        nodes_by_id: dict[UUID, ContractNode],
        tree: ContractNodeTreeIndex,
        organization_id: UUID,
        actor_user_id: UUID,
    ) -> None:
        node = nodes_by_id.get(update.contract_node_id)
        if not node:
            raise ValueError(f"Contract node {update.contract_node_id} not found")

        if node.contract_id != contract.id:
            raise ValueError(f"Node {node.code} does not belong to contract {contract.code}")

        if not tree.is_leaf(node):
            raise ValueError(f"Progress can be set only on leaf nodes ({node.code})")

        if not node.is_active:
            raise ValueError(f"Cannot set progress on inactive node ({node.code})")

        if not (Decimal("0") <= update.progress <= Decimal("1")):
            raise ValueError(f"Invalid progress value {update.progress} for node {node.code}")

        current_progress = node.progress_at(update.progress_date)
        if current_progress is not None and update.progress < current_progress:
            raise ValueError(f"Progress cannot decrease for node {node.code}")

        if node.progress_history.get(update.progress_date) is not None:
            raise ValueError(f"Progress already set for node {node.code} on {update.progress_date}")

        progress_entity = ContractNodeProgress(
            id=self._id_generator(),
            organization_id=organization_id,
            contract_node_id=node.id,
            progress=update.progress,
            progress_date=update.progress_date,
            created_at=self._clock(),
            created_by_user_id=actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
        )

        node_repo.add_progress(progress_entity)

    @staticmethod
    def _get_contract( *, organization_id: UUID, contract_id: UUID,contract_repo:ContractRepository) -> Contract:
        contract = contract_repo.get(
            organization_id=organization_id,
            contract_id=contract_id,
        )
        if contract is None:
            raise ValueError("Contract does not exist")
        return contract
