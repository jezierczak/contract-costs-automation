import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id

from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import DocumentAssignmentFileManager

logger = logging.getLogger(__name__)

def build_apply_documents(subparsers):
    p = subparsers.add_parser(
        "documents",
        help="Apply documents managed from Excel",
    )


    p.set_defaults(handler=handle_apply_documents)

REGISTRY.register_group("apply", build_apply_documents)

def handle_apply_documents(args) -> None:
    services = get_services()
    # ref = args.ref
    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    file_manager = DocumentAssignmentFileManager(
        organization_id=organization_id
    )

    excel_path = file_manager.get_active_file()

    commands = services.document_action_excel_loader_service.load(
        excel_path=excel_path,
        organization_id=organization_id,
        actor_user_id =actor_user_id
    )
    if not commands:
        logger.info("No document decisions found.")
        return
    errors = 0
    logger.info(f"Processing {len(commands)} document decisions...")
    for cmd in commands:
        try:
            services.apply_document_service.execute(cmd=cmd)
        except Exception as e:
            errors += 1
            logger.exception(f"Document {cmd.document_id} failed")


    if errors == 0:
        file_manager.mark_processed()
        logger.info("✔ All documents applied successfully.")
    else:
        logger.error(f"⚠ {errors} errors detected. File NOT marked as processed.")



