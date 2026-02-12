from decimal import Decimal
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.contract import ContractType
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex
from contract_costs.services.contracts.query.dto.contract_list_dto import ContractListDTO
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery


class ListContractsQueryService(ActionHandler[ListContractsQuery,list[ContractListDTO]]):

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
        query: ListContractsQuery,
    ) -> list[ContractListDTO]:

        contracts = self._contract_repo.list_contracts(
            organization_id=query.organization_id,
            contract_type=query.contract_type or ContractType.PROJECT
        )

        vt_direction = self._load_value_type_directions(
            organization_id=query.organization_id
        )

        result: list[ContractListDTO] = []

        for contract in contracts:

            nodes = self._node_repo.list_by_contract(
                contract_id=contract.id,
                organization_id=query.organization_id,
            )

            if not nodes:
                continue

            tree = ContractNodeTreeIndex(nodes)

            planned_budget = self._calculate_planned_budget(tree)
            progress = self._calculate_root_progress(tree)

            financials = self._aggregate_financials(
                organization_id=query.organization_id,
                contract_id=contract.id,
                vt_direction=vt_direction,
            )

            result.append(
                self._build_dto(
                    contract=contract,
                    planned_budget=planned_budget,
                    progress=progress,
                    financials=financials,
                )
            )

        return result

    # =====================================================
    # VALUE TYPES
    # =====================================================

    def _load_value_type_directions(
        self,
        *,
        organization_id: UUID,
    ) -> dict[UUID, ValueDirection]:

        value_types = self._value_type_repo.list_all(
            organization_id=organization_id
        )

        return {
            vt.id: vt.direction
            for vt in value_types
        }

    # =====================================================
    # BUDGET
    # =====================================================

    @staticmethod
    def _calculate_planned_budget(
        tree: ContractNodeTreeIndex,
    ) -> Decimal:

        return sum(
            (n.budget or Decimal("0") for n in tree.leaves()),
            Decimal("0"),
        )

    # =====================================================
    # PROGRESS
    # =====================================================

    @staticmethod
    def _calculate_root_progress(
        tree: ContractNodeTreeIndex,
    ) -> Decimal | None:

        weighted_sum = Decimal("0")
        total_budget = Decimal("0")

        for leaf in tree.leaves():
            if leaf.budget is None or leaf.progress is None:
                continue

            weighted_sum += leaf.budget * leaf.progress
            total_budget += leaf.budget

        if total_budget == 0:
            return None

        return weighted_sum / total_budget

    # =====================================================
    # FINANCIALS
    # =====================================================

    def _aggregate_financials(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
        vt_direction: dict[UUID, ValueDirection],
    ) -> dict[str, Decimal]:

        invoice_lines = self._record_line_repo.list_by_contract(
            contract_id=contract_id,
            organization_id=organization_id,
        )

        net_cost = Decimal("0")
        revenue = Decimal("0")
        gross = Decimal("0")
        non_deductible = Decimal("0")
        revenue_non_deductible = Decimal("0")

        for line in invoice_lines:
            if not line.amount or not line.value_type_id:
                continue

            direction = vt_direction.get(line.value_type_id)
            if not direction:
                continue

            amt = line.amount
            gross += amt.gross

            if direction == ValueDirection.COST:
                net_cost += amt.net
                non_deductible += amt.non_tax_cost

            elif direction == ValueDirection.REVENUE:
                revenue += amt.net
                revenue_non_deductible += amt.non_tax_cost

        return {
            "net": net_cost,
            "gross": gross,
            "non_deduction": non_deductible,
            "revenue": revenue,
            "revenue_non_deductible": revenue_non_deductible,
        }

    # =====================================================
    # DTO
    # =====================================================

    @staticmethod
    def _build_dto(
        *,
        contract,
        planned_budget: Decimal,
        progress: Decimal | None,
        financials: dict[str, Decimal],
    ) -> ContractListDTO:

        return ContractListDTO(
            contract_id=contract.id,
            code=contract.code,
            name=contract.name,
            is_active=contract.is_active,
            planned_budget=planned_budget,
            progress=progress,
            net=financials["net"],
            gross=financials["gross"],
            non_deduction=financials["non_deduction"],
            revenue=financials["revenue"],
            revenue_non_deductible=financials["revenue_non_deductible"],
        )
