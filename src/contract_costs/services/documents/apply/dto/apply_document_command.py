from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType

from contract_costs.action_bus.command import Command
# from contract_costs.action_bus.requires_role import requires_role




class DocumentApplyAction(Enum):
    CREATE_NEW = "CREATE_NEW"
    ADD_TO_EXISTING = "ADD_TO_EXISTING"
    SKIP = "SKIP"
    DELETE = "DELETE"

# @requires_role(OrganizationRole.OWNER, OrganizationRole.ADMIN,OrganizationRole.USER)
@action_type(ActionType.APPLY_DOCUMENT)
@dataclass(frozen=True)
class ApplyDocumentCommand(Command):
    """
    Final decision step for prepared document.

    User-reviewed action applied to a parsed document.
    """

    document_id: UUID

    # CREATE_NEW / ADD_TO_EXISTING / SKIP / DELETE
    action: DocumentApplyAction

    # Required only when action == ADD_TO_EXISTING
    target_record_id: UUID | None = None

    # Optional overrides (user corrections from Excel)
    override_document_type: str | None = None
    override_document_number: str | None = None
    override_seller_nip: str | None = None

    # @property
    # def action_type(self) -> ActionType:
    #     return ActionType.APPLY_DOCUMENT
