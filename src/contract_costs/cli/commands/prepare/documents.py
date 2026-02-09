import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import DocumentAssignmentFileManager

logger = logging.getLogger(__name__)

def build_prepare_documents(subparsers):
    p = subparsers.add_parser(
        "documents",
        help="Prepare documents workflows",
    )

    p.set_defaults(handler=handle_prepare_documents)



REGISTRY.register_group("prepare", build_prepare_documents)

def handle_prepare_documents(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    file_manager = DocumentAssignmentFileManager(
        organization_id=organization_id
    )
    output_path = file_manager.prepare_target()

    bundle = services.prepare_documents_service.execute(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
    )

    services.export_document_assignment_excel_service.execute(
        organization_id=organization_id,
        bundle=bundle,
        output_path=output_path,
    )

    logger.info(
        "Documents prepared for assignment (org=%s): %s",
        organization_id,
        output_path,
    )
