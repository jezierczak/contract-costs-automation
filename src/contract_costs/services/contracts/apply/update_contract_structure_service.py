from dataclasses import replace
from uuid import UUID
import logging

from contract_costs.builders.contract_node_tree_builder import ContractNodeTreeBuilder
from contract_costs.model.contract import Contract, ContractStarter
from contract_costs.model.contract_node import ContractNodeInput, ContractNode
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.services.contracts.validators.contract_node_tree_validator import ContractNodeEntityValidator


logger = logging.getLogger(__name__)


class UpdateContractStructureService:
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
    ) -> None:
        self._contract_repository = contract_repository
        self._contract_node_repository = contract_node_repository
        self._builder = contract_node_tree_builder
        self._contract_node_tree_validator = contract_node_tree_validator

    def execute(
            self,
            contract_id: UUID,
            contract_starter: ContractStarter,
            contract_node_input: list[ContractNodeInput],
    ) -> None:
        logger.info(
            "Updating contract structure: contract_id=%s, nodes_in_excel=%d",
            contract_id,
            len(contract_node_input),
        )

        contract = self._get_contract(contract_id)


        path = contract_starter["path"]

        updated_contract = (
            replace(
                contract,
                name=contract_starter["name"],
                description=contract_starter["description"],
                start_date=contract_starter["start_date"],
                end_date=contract_starter["end_date"],
                budget=contract_starter["budget"],
                status=contract_starter["status"],
                path=path,
            )
            if path is not None
            else replace(
                contract,
                name=contract_starter["name"],
                description=contract_starter["description"],
                start_date=contract_starter["start_date"],
                end_date=contract_starter["end_date"],
                budget=contract_starter["budget"],
                status=contract_starter["status"],
            )
        )

        existing_nodes = self._contract_node_repository.list_by_contract(contract_id)

        if not self._contract_node_repository.has_values(contract_id):
            logger.info(
                "Using HARD replace strategy for contract_id=%s (no existing costs)",
                contract_id,
            )
            self._replace_structure_hard(contract_id, contract_node_input)
        else:
            logger.info(
                "Using SAFE replace strategy for contract_id=%s (existing costs detected)",
                contract_id,
            )
            self._replace_structure_safe(
                contract_id=contract_id,
                contract_node_input=contract_node_input,
                existing_nodes=existing_nodes,
            )

        self._contract_repository.update(updated_contract)

    def _replace_structure_hard(self, contract_id: UUID, cost_node_input: list[ContractNodeInput]) -> None:
        # --- usuń starą strukturę kosztów ---
        logger.warning(
            "HARD replace: deleting all contract nodes for contract_id=%s",
            contract_id,
        )

        self._contract_node_repository.delete_by_contract(contract_id)

        # --- zbuduj nową strukturę ---
        new_contract_nodes = self._builder.build(
            contract_id,
            cost_node_input)

        self._contract_node_tree_validator.validate(new_contract_nodes)
        # --- zapisz wszystko ---

        self._contract_node_repository.add_all(new_contract_nodes)
        logger.info(
            "HARD replace completed: inserted_contract_nodes=%d for contract_id=%s",
            len(new_contract_nodes),
            contract_id,
        )

    def _replace_structure_safe(
            self,
            *,
            contract_id: UUID,
            contract_node_input: list[ContractNodeInput],
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
            contract_id,
            len(existing_nodes),
        )
        existing_by_code = {n.code: n for n in existing_nodes}

        # builder MUSI umieć reuse UUID po code
        new_nodes = self._builder.build(
            contract_id=contract_id,
            contract_node_input=contract_node_input,
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
                if self._contract_node_repository.node_has_values(old_node.id):
                    logger.error(
                        "SAFE replace blocked: contract node '%s' has existing costs (contract_id=%s)",
                        code,
                        contract_id,
                    )
                    raise ValueError(
                        f"Cannot remove contract node '{code}' – costs already exist"
                    )
                to_delete.append(old_node.id)
        logger.info(
            "SAFE replace summary for contract_id=%s: update=%d, insert=%d, delete=%d",
            contract_id,
            len(to_update),
            len(to_insert),
            len(to_delete),
        )
        # --- persist ---
        if to_delete:
            self._contract_node_repository.delete_many(to_delete)

        if to_update:
            self._contract_node_repository.update_many(to_update)

        if to_insert:
            self._contract_node_repository.add_all(to_insert)

        logger.info(
            "Contract metadata updated successfully: contract_id=%s",
            contract_id,
        )

    def _get_contract(self, contract_id: UUID) -> Contract:
        contract = self._contract_repository.get(contract_id)
        if contract is None:
            raise ValueError("Contract does not exist")
        return contract
