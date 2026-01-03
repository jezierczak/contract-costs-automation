import argparse
from contract_costs.cli.registry import REGISTRY
# 🔥 This import triggers registration of CLI commands
import contract_costs.cli.commands  # noqa

def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="contract-costs",
        description="Contract costs management CLI",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---------- SIMPLE COMMANDS ----------
    for name, handler in REGISTRY.simples():
        p = subparsers.add_parser(name)
        p.set_defaults(handler=handler)

    # ---------- GROUP COMMANDS ----------
    for group, builders in REGISTRY.groups():
        group_parser = subparsers.add_parser(group)
        group_sub = group_parser.add_subparsers(dest="entity", required=True)

        for builder in builders:
            builder(group_sub)

    return parser
