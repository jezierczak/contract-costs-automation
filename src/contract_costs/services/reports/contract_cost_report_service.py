from typing import Iterable
from uuid import UUID

from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.repository.cost_node_repository import CostNodeRepository
from contract_costs.repository.cost_type_repository import CostTypeRepository


class ContractCostReportService:

    def __init__(
        self,
        contract_repository: ContractRepository,
        invoice_line_repository: InvoiceLineRepository,
        cost_node_repository: CostNodeRepository,
        cost_type_repository: CostTypeRepository,
    ):
        self._contracts = contract_repository
        self._invoice_lines = invoice_line_repository
        self._cost_nodes = cost_node_repository
        self._cost_types = cost_type_repository

    def generate_rows(self, contract_id: UUID) -> list[dict]:
        contract = self._contracts.get(contract_id)
        if contract is None:
            raise ValueError("Contract does not exist")

        # --- cost nodes ---
        cost_nodes = self._cost_nodes.list_by_contract(contract_id)
        leaf_nodes = self._leaf_nodes(cost_nodes)
        leaf_by_id = {n.id: n for n in leaf_nodes}

        # --- invoice lines ---
        lines = [
            line
            for line in self._invoice_lines.list_lines()
            if line.contract_id == contract_id
        ]

        cost_types = {ct.id: ct for ct in self._cost_types.list()}

        rows: list[dict] = []

        for line in lines:
            if line.cost_node_id not in leaf_by_id:
                continue  # tylko leaf
            if line.cost_node_id is None:
                continue
            if line.cost_node_id not in leaf_by_id:
                continue
            node = leaf_by_id[line.cost_node_id]
            cost_type = cost_types.get(line.cost_type_id)

            rows.append(
                {
                    # --- contract ---
                    "contract_id": contract.id,
                    "contract_code": contract.code,
                    "contract_name": contract.name,

                    # --- cost node ---
                    "cost_node_id": node.id,
                    "cost_node_code": node.code,
                    "cost_node_name": node.name,
                    "cost_node_budget": node.budget,

                    # --- cost type ---
                    "cost_type_code": cost_type.code if cost_type else None,
                    "cost_type_name": cost_type.name if cost_type else None,

                    # --- amounts ---
                    "quantity": line.quantity,
                    "unit": line.unit.value,
                    "net_amount": line.amount.net,
                    "vat_amount": line.amount.tax,
                    "gross_amount": line.amount.gross,
                    "non_tax_amount": line.amount.non_tax_cost
                }
            )

        return rows

    @staticmethod
    def _leaf_nodes(nodes: Iterable) -> list:
        parents = {n.parent_id for n in nodes if n.parent_id}
        return [n for n in nodes if n.id not in parents]
