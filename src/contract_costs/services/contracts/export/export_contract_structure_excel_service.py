from pathlib import Path

from contract_costs.services.contracts.export.contract_structure_excel_generator import ContractStructureExcelGenerator
from contract_costs.services.contracts.export.dto.contract_structure_bundle import ContractStructureBundle


class ExportContractStructureExcelService:
    def __init__(self, excel: ContractStructureExcelGenerator) -> None:
        self._excel = excel
    def execute(
        self,
        bundle: ContractStructureBundle,
        output_path: Path,
    ) -> None:
        self._excel.generate(
            contract_row=bundle.contract,
            cost_node_rows=bundle.cost_nodes,
            output_path=output_path,
        )
