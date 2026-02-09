import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.init.init_application_service import (
    InitApplicationService,
)
from contract_costs.config import WORK_DIR

logger = logging.getLogger(__name__)
from contract_costs.cli.registry import REGISTRY

def handle_init(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
    except ContextError:
        return

    logger.info("Initializing application for organization: %s", organization_id)

    service = InitApplicationService()
    service.execute(organization_id=organization_id)

    logger.info(
        "Application initialized in: %s",
        WORK_DIR / str(organization_id),
    )

REGISTRY.register_simple("init;Initiates folder infrastructure for project.", handle_init)
