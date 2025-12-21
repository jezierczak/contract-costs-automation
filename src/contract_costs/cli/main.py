import argparse
import sys

from contract_costs.cli.commands.add_company import handle_add_company
from contract_costs.cli.commands.edit_company import handle_edit_company
from contract_costs.cli.commands.add_cost_type import handle_add_cost_type
from contract_costs.cli.commands.add_contract import handle_add_contract
from contract_costs.cli.commands.init import handle_init
from contract_costs.cli.commands.run import handle_run


# kolejne importy będziemy dodawać stopniowo:
# from contract_costs.cli.commands.edit_company import handle_edit_company
# from contract_costs.cli.commands.add_contract import handle_add_contract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contract-costs",
        description="Contract costs management CLI",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize application environment")
    subparsers.add_parser("run", help="Run invoice watcher")

    # ---- add ----
    add_parser = subparsers.add_parser("add", help="Add new entity")
    add_sub = add_parser.add_subparsers(dest="entity", required=True)

    add_sub.add_parser("company", help="Add company")
    add_sub.add_parser("contract", help="Add contract")
    add_sub.add_parser("cost-type", help="Add cost type")

    # ---- edit (placeholder) ----
    edit_parser = subparsers.add_parser("edit", help="Edit existing entity")
    edit_sub = edit_parser.add_subparsers(dest="entity", required=True)

    edit_sub.add_parser("company", help="Edit existing companies")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # ---------- ROUTING ----------
    if args.command == "init":
        handle_init()
        return

    if args.command == "run":
        handle_run()
        return

    if args.command == "add" and args.entity == "company":
        handle_add_company()
        return

    if args.command == "add" and args.entity == "contract":
        handle_add_contract()
        return

    if args.command == "add" and args.entity == "cost-type":
        handle_add_cost_type()
        return

    if args.command == "edit" and args.entity == "company":
        handle_edit_company()
        return


    # fallback (nie powinno się zdarzyć)
    parser.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])
