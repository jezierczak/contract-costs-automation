from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command
from contract_costs.model.document import DocumentType, Document


@dataclass(frozen=True,slots=True)
@action_type(ActionType.CREATE_FINANCIAL_RECORD)
class CreateRecordFromDocumentCommand(Command):
    document:Document
    override_reference:str | None
    override_seller_nip:str | None
    override_document_type:DocumentType | None
