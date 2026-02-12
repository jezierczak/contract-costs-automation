from collections import defaultdict
from decimal import Decimal
from uuid import UUID
from datetime import date

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex
from contract_costs.services.contracts.query.contract_details.contract_details_query_command import (
    ContractDetailsQuery,
)
from contract_costs.services.contracts.query.dto.contract_details_dto import (
    ContractDetailsDTO,
)
from contract_costs.services.contracts.query.dto.contract_node_details_dto import (
    ContractNodeDetailsDTO,
)


class ContractDetailsQueryService(ActionHandler[ContractDetailsQuery,ContractDetailsDTO]):

    def __init__(
        self,
        *,
        contract_repo: ContractRepository,
        contract_node_repo: ContractNodeRepository,
        record_line_repo: FinancialRecordLineRepository,
        value_type_repo: ValueTypeRepository,
    ) -> None:
        self._contract_repo = contract_repo
        self._node_repo = contract_node_repo
        self._record_line_repo = record_line_repo
        self._value_type_repo = value_type_repo

    # =====================================================
    # PUBLIC API
    # =====================================================

    def execute(
        self,
        query: ContractDetailsQuery,
    ) -> ContractDetailsDTO:

        contract = self._get_contract(query)

        nodes = self._node_repo.list_by_contract(
            organization_id=query.organization_id,
            contract_id=query.contract_id,
        )

        tree = ContractNodeTreeIndex(nodes)

        planned_budget, progress_map = self._calculate_budget_and_progress(
            tree=tree,
            at_date=query.at_date,
        )

        values = self._aggregate_financials(
            organization_id=query.organization_id,
            contract_id=query.contract_id,
            tree=tree,
        )

        node_dtos = self._build_node_dtos(
            tree=tree,
            planned_budget=planned_budget,
            progress_map=progress_map,
            values=values,
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
        )

    # =====================================================
    # AGGREGATION: BUDGET + PROGRESS
    # =====================================================

    def _calculate_budget_and_progress(
        self,
        *,
        tree: ContractNodeTreeIndex,
        at_date: date | None,
    ) -> tuple[
        dict[UUID, Decimal],
        dict[UUID, Decimal | None],
    ]:

        planned_budget: dict[UUID, Decimal] = {}
        progress_map: dict[UUID, Decimal | None] = {}

        # --- initialize leaves ---
        for node in tree.leaves():
            planned_budget[node.id] = node.budget or Decimal("0")
            progress_map[node.id] = (
                node.progress_at(at_date)
                if at_date
                else node.progress
            )

        # --- rollup ---
        for node in tree.postorder():
            if tree.is_leaf(node):
                continue

            children = tree.children_of(node.id)

            total_budget = sum(
                (planned_budget[c.id] for c in children),
                Decimal("0"),
            )

            planned_budget[node.id] = total_budget

            if total_budget > 0:
                weighted = sum(
                    planned_budget[c.id] * (progress_map[c.id] or Decimal("0"))
                    for c in children
                )
                progress_map[node.id] = weighted / total_budget
            else:
                progress_map[node.id] = None

        return planned_budget, progress_map

    # =====================================================
    # AGGREGATION: FINANCIALS
    # =====================================================

    def _aggregate_financials(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
        tree: ContractNodeTreeIndex,
    ) -> dict[UUID, dict[str, Decimal]]:

        value_types = self._value_type_repo.list_all(
            organization_id=organization_id
        )

        vt_direction = {
            vt.id: vt.direction
            for vt in value_types
        }

        record_lines = self._record_line_repo.list_by_contract(
            organization_id=organization_id,
            contract_id=contract_id,
        )

        values: dict[UUID, dict[str, Decimal]] = defaultdict(
            lambda: {
                "net": Decimal("0"),
                "non_deductible": Decimal("0"),
                "revenue": Decimal("0"),
                "revenue_non_deductible": Decimal("0"),
            }
        )

        # --- aggregate leaves ---
        for line in record_lines:
            if (
                line.contract_node_id is None
                or line.value_type_id is None
                or line.amount is None
            ):
                continue

            direction = vt_direction.get(line.value_type_id)
            if not direction:
                continue

            node_id = line.contract_node_id
            amt = line.amount

            if direction == ValueDirection.COST:
                values[node_id]["net"] += amt.net
                values[node_id]["non_deductible"] += amt.non_tax_cost

            elif direction == ValueDirection.REVENUE:
                values[node_id]["revenue"] += amt.net
                values[node_id]["revenue_non_deductible"] += amt.non_tax_cost

        # --- rollup ---
        for node in tree.postorder():
            if tree.is_leaf(node):
                continue

            children = tree.children_of(node.id)

            for child in children:
                values[node.id]["net"] += values[child.id]["net"]
                values[node.id]["non_deductible"] += values[child.id]["non_deductible"]
                values[node.id]["revenue"] += values[child.id]["revenue"]
                values[node.id]["revenue_non_deductible"] += values[child.id]["revenue_non_deductible"]

        return values

    # =====================================================
    # DTO BUILD
    # =====================================================

    def _build_node_dtos(
        self,
        *,
        tree: ContractNodeTreeIndex,
        planned_budget: dict[UUID, Decimal],
        progress_map: dict[UUID, Decimal | None],
        values: dict[UUID, dict[str, Decimal]],
    ) -> list[ContractNodeDetailsDTO]:

        result: list[ContractNodeDetailsDTO] = []

        for node in tree.all_nodes():
            result.append(
                ContractNodeDetailsDTO(
                    node_id=node.id,
                    parent_id=node.parent_id,
                    code=node.code,
                    name=node.name,
                    is_active=node.is_active,
                    is_leaf=tree.is_leaf(node),
                    planned_budget=planned_budget[node.id],
                    progress=progress_map[node.id],
                    net=values[node.id]["net"],
                    non_deductible=values[node.id]["non_deductible"],
                    revenue=values[node.id]["revenue"],
                    revenue_non_deductible=values[node.id]["revenue_non_deductible"],
                )
            )

        return result

    # =====================================================
    # HELPERS
    # =====================================================

    def _get_contract(
        self,
        query: ContractDetailsQuery,
    ):
        contract = self._contract_repo.get(
            organization_id=query.organization_id,
            contract_id=query.contract_id,
        )

        if contract is None:
            raise ValueError("Contract not found")

        return contract
