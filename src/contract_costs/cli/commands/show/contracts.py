import logging
from collections import defaultdict
from uuid import UUID

import contract_costs.config as cfg

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.infrastructure.excel.contracts.contract_cost_node_tree_excel_exporter import \
    ContractTreeExcelExporter
from contract_costs.infrastructure.filesystem.show_file_manager import ContractsShowFileManager
from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode
from contract_costs.services.contracts.prepare.mappers.contract_node_prepare_mapper import ContractNodePrepareMapper

logger = logging.getLogger(__name__)


def build_show_contracts(subparsers):
    p = subparsers.add_parser(
        "contracts",
        help="Show contracts",
    )

    p.add_argument(
        "ref",
        nargs="?",
        help="Contract UUID or code",
    )

    p.add_argument(
        "--excel",
        action="store_true",
        help="Export contract tree to Excel (read-only)",
    )

    p.add_argument(
        "--active",
        action="store_true",
        help="Show only active contracts",
    )



    p.set_defaults(handler=handle_show_contracts)


def handle_show_contracts(args) -> None:
    services = get_services()
    repo = services.contract_repository
    node_repo = services.contract_node_repository

    # ---------- SINGLE CONTRACT ----------
    if args.ref:
        contract = _resolve_contract(args.ref, repo)
        if not contract:
            print(f"No contract found for ref: {args.ref}")
            return

        if args.excel:
            exporter = ContractTreeExcelExporter()

            fm = ContractsShowFileManager(contract_code=contract.code)
            output_path = fm.create_output_file()

            exporter.export(
                contract=contract,
                cost_nodes=node_repo.list_by_contract(contract.id),
                output_path=output_path,
            )
            print(f"Contract tree exported to Excel: {output_path}")
            return

        print("Contract details:")
        print(f"ID:        {contract.id}")
        print(f"Code:      {contract.code}")
        print(f"Name:      {contract.name}")
        print(f"Active:    {contract.status.value}")
        print(f"Start:     {contract.start_date}")
        print(f"End:       {contract.end_date}")


        print_contract_node_tree(
            nodes_by_parent=ContractNodePrepareMapper.group_by_parent(node_repo.list_by_contract(contract.id)),
        )
        print("- " * 23)
        return

    # ---------- LIST CONTRACTS ----------
    contracts = repo.list()

    if args.active:
        contracts = [c for c in contracts if c.is_active]

    if not contracts:
        print("No contracts found.")
        return

    print(f"{'CODE':<12} {'NAME':<30} {'STATUS'}")
    print("-" * 55)

    for c in contracts:
        print(
            f"{c.code:<12} "
            f"{(c.name or ''):<30} "
            f"{ c.status.value}"
        )




# ---------- utils ----------

def _resolve_contract(ref: str, repo) -> Contract | None:
    try:
        contract = repo.get(UUID(ref))
        if contract:
            return contract
    except ValueError:
        pass

    contract = repo.get_by_code(ref)
    # if contract:
    return contract

    # raise RuntimeError(f"Contract not found: {ref}")


REGISTRY.register_group("show", build_show_contracts)


# def build_nodes_by_parent(
#     nodes: list[CostNode],
# ) -> dict[UUID | None, list[CostNode]]:
#     tree: dict[UUID | None, list[CostNode]] = defaultdict(list)
#
#     for node in nodes:
#         tree[node.parent_id].append(node)
#
#     # opcjonalnie: sortowanie (ładniej się drukuje)
#     for children in tree.values():
#         children.sort(key=lambda n: n.code)
#
#     return tree

def print_contract_node_tree(
    nodes_by_parent: dict[UUID | None, list[ContractNode]],
    parent_id: UUID | None = None,
    prefix: str = "",
    is_last: bool = True,
) -> None:
    children = nodes_by_parent.get(parent_id, [])


    for index, node in enumerate(children):
        last = index == len(children) - 1

        connector = "└── " if last else "├── "
        status = "" if node.is_active else " [INACTIVE]"
        calc_budget = ContractNode.calculate_budget_from_leaves(node.id, nodes_by_parent)
        # budget = f" | budget={node.budget}" if node.budget is not None else ""

        print(f"{prefix}{connector}{node.code} – {node.name} {status}  {calc_budget}"
            
              # f"{CostNode.calculate_budget_from_leaves(node.id,build_nodes_by_parent(children))}"
              # f"{status}"
              f"")

        extension = "    " if last else "│   "
        print_contract_node_tree(
            nodes_by_parent,
            node.id,
            prefix + extension,
            last,
        )

