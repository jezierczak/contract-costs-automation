from dataclasses import dataclass
from pathlib import Path

from contract_costs.action_bus.command import Command
from contract_costs.action_bus.action_type import action_type, ActionType
# # from contract_costs.action_bus.action_type import ActionType
# from contract_costs.action_bus.requires_role import requires_role
# from contract_costs.model.identity.organization_role import OrganizationRole


# @requires_role(OrganizationRole.OWNER, OrganizationRole.ADMIN,OrganizationRole.USER)
@action_type(ActionType.UPLOAD_DOCUMENT)
@dataclass(frozen=True,slots=True)
class UploadDocumentCommand(Command):
    file_path: Path
    ksef_number: str | None = None

