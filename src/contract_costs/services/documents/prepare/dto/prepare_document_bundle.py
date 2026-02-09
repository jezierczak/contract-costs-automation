from dataclasses import dataclass

from contract_costs.services.documents.prepare.dto.prepare_document_dto import PreparedDocumentDto


@dataclass(frozen=True)
class PrepareDocumentsBundle:
    documents: list[PreparedDocumentDto]
