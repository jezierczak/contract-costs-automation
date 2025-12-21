from pathlib import Path
import pandas as pd

from contract_costs.model.contract import ContractStarter, ContractStatus
from contract_costs.model.cost_node import CostNodeInput
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.invoices.company_resolve_service import CompanyResolveService


class ApplyContractStructureExcelService:

    def __init__(
        self,
        create_contract_service: CreateContractService,
        company_resolve_service: CompanyResolveService,
    ) -> None:
        self._create_contract = create_contract_service
        self._company_resolver = company_resolve_service

    def execute(self, excel_path: Path) -> None:
        contract_row, cost_node_rows = self._read_excel(excel_path)

        contract_starter = self._build_contract_starter(contract_row)
        cost_node_tree = self._build_cost_node_tree(cost_node_rows)

        self._create_contract.init(contract_starter)
        self._create_contract.add_cost_node_tree(cost_node_tree)
        self._create_contract.execute()

    @staticmethod
    def _read_excel(path: Path) -> tuple[dict, list[dict]]:
        xls = pd.ExcelFile(path)

        contract_df = pd.read_excel(xls, sheet_name="contract")
        cost_nodes_df = pd.read_excel(xls, sheet_name="cost_nodes")

        if len(contract_df) != 1:
            raise ValueError("Contract sheet must contain exactly one row")

        return (
            contract_df.iloc[0].to_dict(),
            cost_nodes_df.to_dict(orient="records"),
        )

    def _build_contract_starter(self, row: dict) -> ContractStarter:
        owner = self._company_resolver.find_by_tax_number(row["owner_nip"])
        client = self._company_resolver.find_by_tax_number(row["client_nip"])

        return ContractStarter(
            name=row["name"],
            code=row["code"],
            contract_owner=owner,
            client=client,
            description=row.get("description"),
            start_date=row.get("start_date"),
            end_date=row.get("end_date"),
            budget=row.get("budget"),
            path=Path(row["path"]),
            status=ContractStatus[row["status"]],
        )

    @staticmethod
    def _build_cost_node_tree( rows: list[dict]) -> CostNodeInput:
        nodes: dict[str, CostNodeInput] = {}

        for row in rows:
            nodes[row["code"]] = {
                "code": row["code"],
                "name": row["name"],
                "budget": row.get("budget"),
                "quantity": row.get("quantity"),
                "unit": row.get("unit"),
                "children": [],
            }
        roots: list[CostNodeInput] = []

        for row in rows:
            node = nodes[row["code"]]
            parent_code = row.get("parent_code")

            if parent_code:
                nodes[parent_code]["children"].append(node)
            else:
                roots.append(node)

        if len(roots) != 1:
            raise ValueError("Exactly one root cost node is required")

        return roots[0]