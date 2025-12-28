import logging


from contract_costs.services.init.init_application_service import (
    InitApplicationService,
)
from contract_costs.config import WORK_DIR

logger = logging.getLogger(__name__)


def handle_init() -> None:
    logger.info("\nInitializing application...\n")

    service = InitApplicationService()
    service.execute()

    logger.info(f"Application initialized in: {WORK_DIR}")
