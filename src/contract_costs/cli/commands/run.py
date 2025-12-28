from contract_costs.cli.context import get_services
from contract_costs.runner.watcher import run_watcher


def handle_run():
    run_watcher(get_services())