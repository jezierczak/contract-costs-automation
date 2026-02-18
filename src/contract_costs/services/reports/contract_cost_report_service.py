from decimal import Decimal
from typing import Iterable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.reports.dto.generate_contract_cost_report_query import GenerateContractCostReportQuery
from contract_costs.unit_of_work import UnitOfWork


class ContractCostReportService(
    ActionHandler[GenerateContractCostReportQuery, list[dict]]
):

    def execute(
        self,
        *,
        action: GenerateContractCostReportQuery,
        uow: UnitOfWork,
    ) -> list[dict]:

        contract = uow.contracts.get(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )
        if contract is None:
            raise ValueError("Contract does not exist")

        cost_nodes = uow.contract_nodes.list_by_contract(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )
        leaf_nodes = self._leaf_nodes(cost_nodes)
        leaf_by_id = {n.id: n for n in leaf_nodes}

        lines = [
            line
            for line in uow.financial_record_lines.list_all(
                organization_id=action.organization_id
            )
            if line.contract_id == action.contract_id
        ]

        cost_types = {
            ct.id: ct
            for ct in uow.value_types.list_all(
                organization_id=action.organization_id
            )
        }

        rows: list[dict] = []

        for line in lines:
            if not line.contract_node_id:
                continue

            if line.contract_node_id not in leaf_by_id:
                continue

            node = leaf_by_id[line.contract_node_id]
            cost_type = (
                cost_types.get(line.value_type_id)
                if line.value_type_id
                else None
            )

            rows.append(
                {
                    "contract_code": contract.code,
                    "contract_name": contract.name,

                    "cost_node_id": node.id,
                    "cost_node_code": node.code,
                    "cost_node_name": node.name,
                    "cost_node_budget": node.budget,

                    "cost_type_code": cost_type.code if cost_type else None,
                    "cost_type_name": cost_type.name if cost_type else None,

                    "net_amount": line.amount.net or Decimal("0"),
                    "vat_amount": line.amount.tax,
                    "gross_amount": line.amount.gross,
                    "non_tax_amount": line.amount.non_tax_cost,
                }
            )

        return rows

    @staticmethod
    def _leaf_nodes(nodes: Iterable) -> list:
        parents = {n.parent_id for n in nodes if n.parent_id}
        return [n for n in nodes if n.id not in parents]