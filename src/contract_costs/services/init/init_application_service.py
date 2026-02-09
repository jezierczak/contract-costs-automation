from uuid import UUID

from contract_costs.infrastructure.filesystem.workdir_initializer import (
    WorkDirInitializer,
)


class InitApplicationService:
    def __init__(self) -> None:
        self._workdir_initializer = WorkDirInitializer()

    def execute(self,*,organization_id:UUID) -> None:
        self._workdir_initializer.execute(organization_id=organization_id)
