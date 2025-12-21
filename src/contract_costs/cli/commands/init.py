from pathlib import Path

from contract_costs.services.init.init_application_service import (
    InitApplicationService,
)
from contract_costs.config import WORK_DIR


def handle_init() -> None:
    print("\nInitializing application...\n")

    service = InitApplicationService()
    service.execute()

    print(f"Application initialized in: {WORK_DIR}")
