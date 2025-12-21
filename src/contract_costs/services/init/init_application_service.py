from pathlib import Path
from contract_costs.infrastructure.filesystem.workdir_initializer import (
    WorkDirInitializer,
)


class InitApplicationService:
    def __init__(self) -> None:
        self._workdir_initializer = WorkDirInitializer()

    def execute(self) -> None:
        self._workdir_initializer.execute()
