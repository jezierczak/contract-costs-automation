from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.runner.watcher import run_watcher
from contract_costs.cli.registry import REGISTRY


def handle_run(args):
    services = get_services()

    try:
        organization_id=require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    run_watcher(organization_id=organization_id,actor_user_id=actor_user_id,services=services)


REGISTRY.register_simple("run;Starts watching for documents in input folder.", handle_run)
