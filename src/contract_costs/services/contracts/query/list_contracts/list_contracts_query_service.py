from decimal import Decimal
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.financial_record_line_repository import FinancialRecordLineRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex
from contract_costs.services.contracts.query.dto.contract_list_dto import ContractListDTO
from contract_costs.services.contracts.query.list_contracts.list_contracts_query_command import ListContractsQuery
from contract_costs.unit_of_work import UnitOfWork


class ListContractsQueryService(ActionHandler[ListContractsQuery, list[ContractListDTO]]):

    def execute(
        self,
        *,
        action: ListContractsQuery,
        uow: UnitOfWork,
    ) -> list[ContractListDTO]:

        contract_repo = uow.contracts
        node_repo = uow.contract_nodes
        record_line_repo = uow.financial_record_lines
        value_type_repo = uow.value_types

        # contracts = contract_repo.list_contracts(
        #     organization_id=action.organization_id,
        #     contract_type=action.contract_type or ContractType.PROJECT,
        # )

        vt_direction = self._load_value_type_directions(
            organization_id=action.organization_id,
            value_type_repo=value_type_repo
        )

        contracts = contract_repo.list_contracts(
            organization_id=action.organization_id,
            contract_type=action.contract_type,
            status=action.status,
            search=action.search,
        )

        result: list[ContractListDTO] = []

        for contract in contracts:
            nodes = node_repo.list_by_contract(
                contract_id=contract.id,
                organization_id=action.organization_id,
            )
            financials: dict[str, Decimal] = {}

            if not nodes:
                planned_budget = Decimal("0")
                progress = None
                financials["net"] = Decimal("0")
                financials["gross"] = Decimal("0")
                financials["non_deduction"] = Decimal("0")
                financials["revenue"] = Decimal("0")
                financials["revenue_non_deductible"] = Decimal("0")
            else:

                tree = ContractNodeTreeIndex(nodes)
                planned_budget = self._calculate_planned_budget(tree)
                progress = self._calculate_root_progress(tree)

                financials = self._aggregate_financials(
                    organization_id=action.organization_id,
                    contract_id=contract.id,
                    vt_direction=vt_direction,
                    record_line_repo=record_line_repo,
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

    @staticmethod
    def _load_value_type_directions(
        *,
        value_type_repo: ValueTypeRepository,
        organization_id: UUID,
    ) -> dict[UUID, ValueDirection]:
        value_types = value_type_repo.list_all(organization_id=organization_id)
        return {vt.id: vt.direction for vt in value_types}

    @staticmethod
    def _calculate_planned_budget(tree: ContractNodeTreeIndex) -> Decimal:
        return sum((n.budget or Decimal("0") for n in tree.leaves()), Decimal("0"))

    @staticmethod
    def _calculate_root_progress(tree: ContractNodeTreeIndex) -> Decimal | None:
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

    @staticmethod
    def _aggregate_financials(
        *,
        record_line_repo: FinancialRecordLineRepository,
        organization_id: UUID,
        contract_id: UUID,
        vt_direction: dict[UUID, ValueDirection],
    ) -> dict[str, Decimal]:
        invoice_lines = record_line_repo.list_by_contract(
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
