from dataclasses import replace
from uuid import UUID

from contract_costs.builders.cost_node_tree_builder import CostNodeTreeBuilder
from contract_costs.model.contract import Contract, ContractStarter
from contract_costs.model.cost_node import CostNodeInput
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository


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
        cost_node_repository: CostNodeRepository,
        cost_node_tree_builder: CostNodeTreeBuilder,
    ) -> None:
        self._contract_repository = contract_repository
        self._cost_node_repository = cost_node_repository
        self._builder = cost_node_tree_builder

    def execute(
        self,
        contract_id: UUID,
        contract_starter: ContractStarter,
        cost_node_input: CostNodeInput,
    ) -> None:
        # --- 1️⃣ pobierz istniejący kontrakt ---
        contract = self._get_contract(contract_id)

        if self._cost_node_repository.has_costs(contract_id):
            raise ValueError(
                "Cannot update contract structure: invoice costs already exist"
            )

        # --- 2️⃣ update metadata (ID, owner, client zostają) ---
        updated_contract = replace(
            contract,
            name=contract_starter["name"],
            description=contract_starter["description"],
            start_date=contract_starter["start_date"],
            end_date=contract_starter['end_date'],
            budget=contract_starter['budget'],
            path=contract_starter["path"],
            status=contract_starter["status"],
        )

        # --- 3️⃣ usuń starą strukturę kosztów ---
        self._cost_node_repository.delete_by_contract(contract_id)

        # --- 4️⃣ zbuduj nową strukturę ---
        new_cost_nodes = self._builder.build(contract_id, cost_node_input)

        # --- 5️⃣ zapisz wszystko ---
        self._contract_repository.update(updated_contract)
        self._cost_node_repository.add_all(new_cost_nodes)

    def _get_contract(self, contract_id: UUID) -> Contract:
        contract = self._contract_repository.get(contract_id)
        if contract is None:
            raise ValueError("Contract does not exist")
        return contract
