from contract_costs.cli.context import get_services
from contract_costs.runner.watcher import run_watcher
from contract_costs.cli.registry import REGISTRY

# def build_run(subparsers):
#     p = subparsers.add_parser("run", help="Run invoice watcher")
#     p.set_defaults(handler=handle_run)


def handle_run(args):
    run_watcher(get_services())


REGISTRY.register_simple("run", handle_run)
