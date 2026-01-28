from collections import defaultdict
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.contract import ContractStatus
from contract_costs.model.value_direction import ValueDirection
from contract_costs.repository.contract_node_repository import ContractNodeRepository
from contract_costs.repository.contract_repository import ContractRepository
from contract_costs.repository.invoice_line_repository import InvoiceLineRepository
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex
from contract_costs.services.contracts.query.dto.contract_details_dto import ContractDetailsDTO
from contract_costs.services.contracts.query.dto.contract_list_dto import ContractListDTO
from contract_costs.services.contracts.query.dto.contract_node_details_dto import ContractNodeDetailsDTO


class ContractQueryService:

    def __init__(
        self,
        *,
        contract_repo: ContractRepository,
        contract_node_repo: ContractNodeRepository,
        invoice_line_repo: InvoiceLineRepository,
        value_type_repo: ValueTypeRepository,
    ) -> None:
        self._contract_repo = contract_repo
        self._node_repo = contract_node_repo
        self._invoice_line_repo = invoice_line_repo
        self._value_type_repo = value_type_repo

    def list_contracts(self) -> list[ContractListDTO]:
        contracts = self._contract_repo.list()
        value_types = self._value_type_repo.list()

        vt_direction = {
            vt.id: vt.direction
            for vt in value_types
        }

        result: list[ContractListDTO] = []

        for contract in contracts:
            nodes = self._node_repo.list_by_contract(contract.id)
            if not nodes:
                continue

            tree = ContractNodeTreeIndex(nodes)

            # ---------- BUDGET + PROGRESS ----------
            planned_budget = sum(
                (n.budget or Decimal("0") for n in tree.leaves()),
                Decimal("0"),
            )

            progress = self._calculate_root_progress(tree)

            # ---------- FINANCIALS ----------
            invoice_lines = self._invoice_line_repo.list_by_contract(contract.id)

            net_cost = Decimal("0")
            revenue = Decimal("0")
            gross = Decimal("0")
            non_deductible = Decimal("0")

            for line in invoice_lines:
                if not line.amount or not line.value_type_id:
                    continue

                direction = vt_direction.get(line.value_type_id)
                amt = line.amount

                gross += amt.gross
                non_deductible += amt.non_tax_cost

                if direction == ValueDirection.COST:
                    net_cost += amt.net
                elif direction == ValueDirection.REVENUE:
                    revenue += amt.net

            result.append(
                ContractListDTO(
                    contract_id=contract.id,
                    code=contract.code,
                    name=contract.name,
                    is_active=contract.is_active,
                    planned_budget=planned_budget,
                    progress=progress,
                    net=net_cost,
                    gross=gross,
                    non_deduction=non_deductible,
                    revenue=revenue,
                )
            )

        return result

    def get_contract_details(
            self,
            *,
            contract_id: UUID,
            at_date: date | None = None,
    ) -> ContractDetailsDTO:

        contract = self._contract_repo.get(contract_id)
        if not contract:
            raise ValueError("Contract not found")

        planned_budget: dict[UUID, Decimal] = {}
        progress_map: dict[UUID, Decimal | None] = {}

        nodes = self._node_repo.list_by_contract(contract_id)
        tree = ContractNodeTreeIndex(nodes)

        for node in tree.leaves():
            planned_budget[node.id] = node.budget or Decimal("0")
            progress_map[node.id] = node.progress_at(at_date) if at_date else node.progress

        value_types = self._value_type_repo.list()
        vt_direction = {vt.id: vt.direction for vt in value_types}

        invoice_lines = self._invoice_line_repo.list_by_contract(contract_id)

        # ---------- AGG STRUCTURES ----------
        values = defaultdict(lambda: {
            "net": Decimal("0"),
            "gross": Decimal("0"),
            "non_deductible": Decimal("0"),
            "revenue": Decimal("0"),
        })

        for line in invoice_lines:
            if not line.contract_node_id or not line.amount:
                continue

            node_id = line.contract_node_id
            direction = vt_direction.get(line.value_type_id)

            amt = line.amount
            # values[node_id]["gross"] += amt.gross
            values[node_id]["non_deductible"] += amt.non_tax_cost

            if direction == ValueDirection.COST:
                values[node_id]["net"] += amt.net
            elif direction == ValueDirection.REVENUE:
                values[node_id]["revenue"] += amt.net

        for node in tree.postorder():
            if tree.is_leaf(node):
                continue

            children = tree.children_of(node.id)

            for child in children:
                values[node.id]["net"] += values[child.id]["net"]
                values[node.id]["non_deductible"] += values[child.id]["non_deductible"]
                values[node.id]["revenue"] += values[child.id]["revenue"]

            total_budget = sum((
                planned_budget[c.id] for c in children
            ),Decimal("0"))

            planned_budget[node.id] = total_budget

            if total_budget > 0:
                weighted = sum(
                    planned_budget[c.id] * (progress_map[c.id] or Decimal("0"))
                    for c in children
                )
                progress_map[node.id] = weighted / total_budget
            else:
                progress_map[node.id] = None

        node_dtos: list[ContractNodeDetailsDTO] = []

        for node in tree.all_nodes():
            progress = (
                node.progress_at(at_date)
                if at_date
                else node.progress
            )

            node_dtos.append(
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
                )
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

    @staticmethod
    def _calculate_root_progress(
        tree: ContractNodeTreeIndex,
    ) -> Decimal | None:
        leaves = tree.leaves()

        weighted_sum = Decimal("0")
        total_budget = Decimal("0")

        for leaf in leaves:
            if leaf.budget is None or leaf.progress is None:
                continue

            weighted_sum += leaf.budget * leaf.progress
            total_budget += leaf.budget

        if total_budget == 0:
            return None

        return weighted_sum / total_budget
