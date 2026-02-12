from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.document_resolver import resolve_document_id
from contract_costs.services.documents.process.delete.delete_document_command import DeleteDocumentCommand
from contract_costs.services.documents.process.reprocess.reprocess_document_command import ReprocessDocumentCommand


def build_documents_commands(subparsers):
    p = subparsers.add_parser(
        "reprocess",
        help="Reprocess document",
    )
    # REPROCESS
    p.add_argument("--id", required=True, help="Document UUID")
    p.add_argument("--force", required=False,action="store_true", help="Force reprocess if payload exists")
    p.set_defaults(handler=handle_reprocess_document)

    # DELETE
    p_del = subparsers.add_parser(
        "delete",
        help="Delete document",
    )
    p_del.add_argument("--id", required=True, help="Document UUID")
    p_del.set_defaults(handler=handle_delete_document)

REGISTRY.register_group("documents", build_documents_commands)



from uuid import UUID
from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError


def handle_reprocess_document(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return None

    document_id = resolve_document_id(
        repository=services.document_repository,
        organization_id=organization_id,
        raw_id=args.id,
    )
    # if args.force:
    #     has_payload = True

    services.action_bus.execute(
        action=ReprocessDocumentCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            document_id=document_id,
            force=args.force,
        ),
        handler=services.reprocess_document_service
    )

    print("Document reprocessed.")


def handle_delete_document(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return None

    document_id = resolve_document_id(
        repository=services.document_repository,
        organization_id=organization_id,
        raw_id=args.id,
    )

    services.action_bus.execute(
        action=DeleteDocumentCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            document_id=document_id,
        ),
        handler=services.delete_document_service
    )

    print("Document deleted.")
