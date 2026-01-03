import logging


from contract_costs.services.init.init_application_service import (
    InitApplicationService,
)
from contract_costs.config import WORK_DIR

logger = logging.getLogger(__name__)
from contract_costs.cli.registry import REGISTRY


# def build_init(subparsers):
#     p = subparsers.add_parser("init", help="Initialize application environment")
#     p.set_defaults(handler=handle_init())
#

def handle_init(args) -> None:
    logger.info("\nInitializing application...\n")

    service = InitApplicationService()
    service.execute()

    logger.info(f"Application initialized in: {WORK_DIR}")

REGISTRY.register_simple("init", handle_init)
