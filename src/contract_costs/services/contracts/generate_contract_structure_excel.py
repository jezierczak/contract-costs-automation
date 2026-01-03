from pathlib import Path
from uuid import UUID

from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.services.contracts.export.contract_structure_excel_generator import ContractStructureExcelGenerator


class GenerateContractStructureExcelService:

    def __init__(
        self,
        contract_repository: ContractRepository,
        cost_node_repository: CostNodeRepository,
        excel_generator: ContractStructureExcelGenerator,
    ) -> None:
        self._contracts = contract_repository
        self._cost_nodes = cost_node_repository
        self._excel = excel_generator

    def generate_empty(self, output_path: Path) -> None:
        self._excel.generate(
            contract_row=None,
            cost_node_rows=[],
            output_path=output_path,
        )

    def generate_from_contract(
        self,
        contract_id: UUID,
        output_path: Path,
    ) -> None:
        contract = self._contracts.get(contract_id)
        if not contract:
            raise Exception(f"Contract with id {contract_id} not found")

        cost_nodes = self._cost_nodes.list_by_contract(contract_id)

        contract_row = ContractStructureExcelGenerator.map_contract_to_row(contract)
        cost_node_rows = ContractStructureExcelGenerator.flatten_cost_nodes(cost_nodes)

        self._excel.generate(
            contract_row=contract_row,
            cost_node_rows=cost_node_rows,
            output_path=output_path,
        )

