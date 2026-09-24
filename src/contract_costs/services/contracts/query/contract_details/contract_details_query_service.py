from collections import defaultdict
from collections.abc import Callable
from decimal import Decimal
from uuid import UUID
from datetime import date

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.services.contracts.financials.contract_financials import ContractFinancials
from contract_costs.services.contracts.financials.contract_financials_calculator import (
    ContractFinancialsCalculator,
)
from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex
from contract_costs.services.contracts.query.contract_details.contract_details_query_command import (
    ContractDetailsQuery,
)
from contract_costs.services.contracts.query.contract_details.contract_node_value_type_breakdown_dto import \
    ContractNodeValueTypeBreakdownDTO
from contract_costs.services.contracts.query.dto.contract_details_dto import (
    ContractDetailsDTO,
)
from contract_costs.services.contracts.query.dto.contract_node_details_dto import (
    ContractNodeDetailsDTO,
)
from contract_costs.unit_of_work import UnitOfWork


class ContractDetailsQueryService(ActionHandler[ContractDetailsQuery,ContractDetailsDTO]):

    def __init__(self, *, today: Callable[[], date] = date.today) -> None:
        self._today = today

    # def __init__(
    #     self,
    #     *,
    #     contract_repo: ContractRepository,
    #     contract_node_repo: ContractNodeRepository,
    #     record_line_repo: FinancialRecordLineRepository,
    #     value_type_repo: ValueTypeRepository,
    # ) -> None:
    #     self._contract_repo = contract_repo
    #     self._node_repo = contract_node_repo
    #     self._record_line_repo = record_line_repo
    #     self._value_type_repo = value_type_repo

    # =====================================================
    # PUBLIC API
    # =====================================================

    def execute(
        self,
        *,
        action: ContractDetailsQuery,
        uow:UnitOfWork
    ) -> ContractDetailsDTO:

        contract_repo = uow.contracts
        node_repo = uow.contract_nodes
        record_line_repo = uow.financial_record_lines
        value_type_repo = uow.value_types

        contract = self._get_contract(contract_repo=contract_repo,query=action)

        nodes = node_repo.list_by_contract(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )

        tree = ContractNodeTreeIndex(nodes)

        financials = ContractFinancialsCalculator.calculate(
            nodes=nodes,
            lines=record_line_repo.list_by_contract(
                organization_id=action.organization_id,
                contract_id=action.contract_id,
            ),
            value_type_directions={
                vt.id: vt.direction
                for vt in value_type_repo.list_all(organization_id=action.organization_id)
            },
            start_date=contract.start_date,
            end_date=contract.end_date,
            today=self._today(),
            at_date=action.at_date,
        )

        breakdown_map = self._aggregate_by_value_type(
            value_type_repo=value_type_repo,
            record_line_repo=record_line_repo,
            organization_id=action.organization_id,
            contract_id=action.contract_id,
            tree=tree,
        )

        node_dtos = self._build_node_dtos(
            tree=tree,
            financials=financials,
            breakdown_map=breakdown_map,
        )

        total = financials.total
        margin = total.result_on_progress
        margin_percent = (
            margin / total.budget
            if margin is not None and total.budget
            else None
        )

        return ContractDetailsDTO(
            contract_id=contract.id,
            code=contract.code,
            name=contract.name,
            description=contract.description,
            status=contract.status.value,
            start_date=contract.start_date,
            end_date=contract.end_date,
            nodes=node_dtos,
            owner=contract.owner,
            client=contract.client,
            budget=total.budget,
            time_progress=financials.indicators.time_progress,
            overall_progress=total.progress,
            executed_value=total.executed,
            cost_total=total.cost.cashflow,
            revenue_total=total.revenue.net,
            margin=margin,
            margin_percent=margin_percent,
            financials=financials,
        )

    # =====================================================
    # DTO BUILD
    # =====================================================
    @staticmethod
    def _build_node_dtos(
        *,
        tree: ContractNodeTreeIndex,
        financials: ContractFinancials,
        breakdown_map: dict[UUID, list[ContractNodeValueTypeBreakdownDTO]]
    ) -> list[ContractNodeDetailsDTO]:

        result: list[ContractNodeDetailsDTO] = []

        for node in tree.preorder():
            node_financials = financials.nodes[node.id]

            result.append(
                ContractNodeDetailsDTO(
                    node_id=node.id,
                    parent_id=node.parent_id,
                    code=node.code,
                    name=node.name,
                    is_active=node.is_active,
                    is_leaf=tree.is_leaf(node),
                    planned_budget=node_financials.budget,
                    progress=node_financials.progress,
                    net=node_financials.cost.net,
                    non_deductible=node_financials.cost.non_tax,
                    revenue=node_financials.revenue.net,
                    revenue_non_deductible=node_financials.revenue.non_tax,
                    level=tree.depth_of(node.id),
                    value_type_breakdown=[v.to_dict() for v in breakdown_map.get(node.id, [])],
                    financials=node_financials,
                )
            )

        return result

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _get_contract(
        *,
        contract_repo: ContractRepository,
        query: ContractDetailsQuery,
    ):
        contract = contract_repo.get(
            organization_id=query.organization_id,
            contract_id=query.contract_id,
        )

        if contract is None:
            raise ValueError("Contract not found")

        return contract

    @staticmethod
    def _aggregate_by_value_type(
            *,
            value_type_repo,
            record_line_repo,
            organization_id: UUID,
            contract_id: UUID,
            tree,
    ) -> dict[UUID, list[ContractNodeValueTypeBreakdownDTO]]:

        # =================================================
        # LOAD VALUE TYPES
        # =================================================
        value_types = value_type_repo.list_all(
            organization_id=organization_id
        )

        vt_map = {v.id: v for v in value_types}

        # structure:
        # node_id -> value_type_id -> values
        values = defaultdict(
            lambda: defaultdict(
                lambda: {
                    "net": Decimal("0"),
                    "non_deductible": Decimal("0"),
                }
            )
        )

        # =================================================
        # 1️⃣ LEAVES AGGREGATION
        # =================================================
        lines = record_line_repo.list_by_contract(
            organization_id=organization_id,
            contract_id=contract_id,
        )

        for line in lines:

            if not line.contract_node_id:
                continue

            if not line.value_type_id:
                continue

            if not line.amount:
                continue

            bucket = values[line.contract_node_id][line.value_type_id]

            bucket["net"] += line.amount.net
            bucket["non_deductible"] += line.amount.non_tax_cost

        # =================================================
        # 2️⃣ TREE ROLLUP (GAŁĘZIE)
        # =================================================
        for node in tree.postorder():

            if tree.is_leaf(node):
                continue

            for child in tree.children_of(node.id):

                for vt_id, vals in values[child.id].items():
                    parent = values[node.id][vt_id]

                    parent["net"] += vals["net"]
                    parent["non_deductible"] += vals["non_deductible"]

        # =================================================
        # 3️⃣ DTO OUTPUT
        # =================================================
        output: dict[UUID, list[ContractNodeValueTypeBreakdownDTO]] = {}

        for node_id, vt_data in values.items():

            output[node_id] = []

            # --- totals per direction ---
            total_cost = Decimal("0")
            total_revenue = Decimal("0")

            for vt_id, vals in vt_data.items():

                vt = vt_map.get(vt_id)
                if not vt:
                    continue

                total = vals["net"] + vals["non_deductible"]

                if vt.direction == ValueDirection.COST:
                    total_cost += total
                else:
                    total_revenue += total

            # --- build DTO list (sorted for stable UI) ---
            sorted_items = sorted(
                vt_data.items(),
                key=lambda x: vt_map[x[0]].code if vt_map.get(x[0]) else "",
            )

            for vt_id, vals in sorted_items:

                vt = vt_map.get(vt_id)
                if not vt:
                    continue

                total = vals["net"] + vals["non_deductible"]

                # percent inside COST / REVENUE group
                if vt.direction == ValueDirection.COST:
                    percent = (
                        (total / total_cost * 100)
                        if total_cost > 0
                        else Decimal("0")
                    )
                else:
                    percent = (
                        (total / total_revenue * 100)
                        if total_revenue > 0
                        else Decimal("0")
                    )

                output[node_id].append(
                    ContractNodeValueTypeBreakdownDTO(
                        value_type_id=vt.id,
                        code=vt.code,
                        name=vt.name,
                        direction=vt.direction.value,
                        net=vals["net"],
                        non_deductible=vals["non_deductible"],
                        total=total,
                        percent_of_direction=percent,
                    )
                )

        return output


    # @staticmethod
    # def _aggregate_by_value_type_all_nodes(
    #         *,
    #         value_type_repo,
    #         record_line_repo,
    #         organization_id: UUID,
    #         contract_id: UUID,
    # ) -> dict[UUID, list[ContractNodeValueTypeBreakdownDTO]]:
    #
    #     value_types = value_type_repo.list_all(
    #         organization_id=organization_id
    #     )
    #
    #     vt_map = {v.id: v for v in value_types}
    #
    #     lines = record_line_repo.list_by_contract(
    #         organization_id=organization_id,
    #         contract_id=contract_id,
    #     )
    #
    #     # node_id -> value_type_id -> values
    #     tmp = defaultdict(lambda: defaultdict(lambda: {
    #         "net": Decimal("0"),
    #         "non_deductible": Decimal("0"),
    #     }))
    #
    #     for line in lines:
    #
    #         if (
    #                 line.contract_node_id is None
    #                 or line.value_type_id is None
    #                 or line.amount is None
    #         ):
    #             continue
    #
    #         vt = vt_map.get(line.value_type_id)
    #         if not vt:
    #             continue
    #
    #         node_id = line.contract_node_id
    #
    #         tmp[node_id][vt.id]["net"] += line.amount.net
    #         tmp[node_id][vt.id]["non_deductible"] += line.amount.non_tax_cost
    #
    #     # ---- build DTO output ----
    #     result: dict[UUID, list[ContractNodeValueTypeBreakdownDTO]] = {}
    #
    #     for node_id, vt_items in tmp.items():
    #
    #         output = []
    #
    #         for vt_id, vals in vt_items.items():
    #             vt = vt_map[vt_id]
    #
    #             output.append(
    #                 ContractNodeValueTypeBreakdownDTO(
    #                     value_type_id=vt.id,
    #                     code=vt.code,
    #                     name=vt.name,
    #                     direction=vt.direction.value,
    #                     net=vals["net"],
    #                     non_deductible=vals["non_deductible"],
    #                     total=vals["net"] + vals["non_deductible"],
    #                 )
    #             )
    #
    #         # opcjonalnie sort po code
    #         output.sort(key=lambda x: x.code)
    #
    #         result[node_id] = output
    #
    #     return result
