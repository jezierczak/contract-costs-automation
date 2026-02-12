from dataclasses import replace
from datetime import datetime
from typing import Callable
from uuid import UUID
import logging

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.contracts.builders.contract_node_tree_builder import ContractNodeTreeBuilder
from contract_costs.common.time import utc_now
from contract_costs.model.contract import Contract
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.services.contracts.apply.command.update_contract_structure_command import \
    UpdateContractStructureCommand
from contract_costs.services.contracts.validators.contract_node_tree_validator import ContractNodeEntityValidator


logger = logging.getLogger(__name__)


class UpdateContractStructureService(ActionHandler[UpdateContractStructureCommand,None]):
    """
    Aktualizuje ISTNIEJĄCY kontrakt na podstawie pełnej struktury
    (Excel = źródło prawdy).

    Strategia:
    - update metadata kontraktu (replace)
    - delete ALL cost nodes
    - rebuild cost node tree
    """

    def __init__(
        self,
        contract_repository: ContractRepository,
        contract_node_repository: ContractNodeRepository,
        contract_node_tree_builder: ContractNodeTreeBuilder,
        contract_node_tree_validator: ContractNodeEntityValidator,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._contract_repository = contract_repository
        self._contract_node_repository = contract_node_repository
        self._builder = contract_node_tree_builder
        self._contract_node_tree_validator = contract_node_tree_validator
        self._clock = clock

    def execute(
            self,
            command: UpdateContractStructureCommand
    ) -> None:
        logger.info(
            "Updating contract structure: contract_id=%s, nodes_in_excel=%d",
            command.contract_id,
            len(command.contract_node_input),
        )

        contract = self._get_contract(
            organization_id=command.organization_id,
            contract_id=command.contract_id,
        )

        updated_contract = replace(
            contract,
            name=command.name,
            description=command.description,
            start_date=command.start_date,
            end_date=command.end_date,
            budget=command.budget,
            status=command.status,
            path=command.path,
            updated_at=self._clock(),
            updated_by_user_id=command.actor_user_id,
        )

        existing_nodes = self._contract_node_repository.list_by_contract(
            contract_id=command.contract_id,
            organization_id=command.organization_id,
        )

        if not self._contract_node_repository.has_values(
                contract_id=command.contract_id,
                organization_id=command.organization_id
        ):
            logger.info(
                "Using HARD replace strategy for contract_id=%s (no existing costs)",
                command.contract_id,
            )
            self._replace_structure_hard(command=command)
        else:
            logger.info(
                "Using SAFE replace strategy for contract_id=%s (existing costs detected)",
                command.contract_id,
            )
            self._replace_structure_safe(
                command=command,
                existing_nodes=existing_nodes,
            )

        self._contract_repository.update(updated_contract)

    # =====================================================
    # REPLACE STRATEGIES
    # =====================================================

    def _replace_structure_hard(
        self,
        *,
        command: UpdateContractStructureCommand,
    ) -> None:
        # --- usuń starą strukturę kosztów ---
        logger.warning(
            "HARD replace: deleting all contract nodes for contract_id=%s",
            command.contract_id,
        )

        self._contract_node_repository.delete_by_contract(
            contract_id=command.contract_id,
            organization_id=command.organization_id,
        )

        # --- zbuduj nową strukturę ---
        new_nodes = self._builder.build(
            organization_id=command.organization_id,
            actor_user_id=command.actor_user_id,
            created_at=self._clock(),
            contract_id=command.contract_id,
            contract_node_input=command.contract_node_input,
        )

        self._contract_node_tree_validator.validate(new_nodes)
        # --- zapisz wszystko ---

        self._contract_node_repository.add_all(new_nodes)
        logger.info(
            "HARD replace completed: inserted_contract_nodes=%d for contract_id=%s",
            len(new_nodes),
            command.contract_id,
        )

    def _replace_structure_safe(
            self,
            *,
            command: UpdateContractStructureCommand,
            existing_nodes: list,
    ) -> None:
        """
        SAFE replace:
        - zachowuje UUID contract nodes z kosztami
        - usuwa tylko te bez kosztów
        - dodaje nowe
        """
        logger.info(
            "SAFE replace started for contract_id=%s, existing_nodes=%d",
            command.contract_id,
            len(existing_nodes),
        )
        existing_by_code = {n.code: n for n in existing_nodes}

        new_nodes = self._builder.build(
            organization_id=command.organization_id,
            actor_user_id=command.actor_user_id,
            created_at=self._clock(),
            contract_id=command.contract_id,
            contract_node_input=command.contract_node_input,
            existing_nodes=existing_by_code,
        )

        self._contract_node_tree_validator.validate(new_nodes)

        # --- podział ---
        new_by_code = {n.code: n for n in new_nodes}

        to_update = []
        to_insert = []
        to_delete = []

        for code, node in new_by_code.items():
            if code in existing_by_code:
                to_update.append(node)
            else:
                to_insert.append(node)

        for code, old_node in existing_by_code.items():
            if code not in new_by_code:
                if self._contract_node_repository.node_has_values(
                        contract_node_id=old_node.id,
                        organization_id=command.organization_id):
                    logger.error(
                        "SAFE replace blocked: contract node '%s' has existing costs (contract_id=%s)",
                        code,
                        command.contract_id,
                    )
                    raise ValueError(
                        f"Cannot remove contract node '{code}' – costs already exist"
                    )
                to_delete.append(old_node.id)
        logger.info(
            "SAFE replace summary for contract_id=%s: update=%d, insert=%d, delete=%d",
            command.contract_id,
            len(to_update),
            len(to_insert),
            len(to_delete),
        )
        # --- persist ---
        if to_delete:
            self._contract_node_repository.delete_many(
                ids=to_delete,
                organization_id=command.organization_id,
            )

        if to_update:
            self._contract_node_repository.update_many(to_update)

        if to_insert:
            self._contract_node_repository.add_all(to_insert)

        logger.info(
            "Contract metadata updated successfully: contract_id=%s",
            command.contract_id,
        )

    def _get_contract(
            self,
            *,
            organization_id: UUID,
            contract_id: UUID,
    ) -> Contract:
        contract = self._contract_repository.get(
            organization_id=organization_id,
            contract_id=contract_id,
        )
        if contract is None:
            raise ValueError("Contract does not exist")
        return contract
