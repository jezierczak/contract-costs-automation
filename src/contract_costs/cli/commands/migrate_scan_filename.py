from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id

from contract_costs.common.context.exceptions import ContextError


def build_migrate_scan(subparsers):
    p = subparsers.add_parser(
        "scan-files",
        help="Migrate scan_filename to documents table",
    )

    p.add_argument(
        "--commit",
        action="store_true",
        help="Execute migration (default is dry-run)",
    )

    p.set_defaults(handler=handle_migrate_scan)


REGISTRY.register_group("migrate", build_migrate_scan)


def handle_migrate_scan(args):

    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    services.migrate_scan_filename_service.migrate(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        dry_run=not args.commit,
    )
