from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True,slots=True)
class PreparedDocumentDto:
    document_id: UUID

    document_source: str   # enum.value
    document_type: str     # enum.value

    document_number: str | None
    seller_nip: str | None

    file_path: str         # relative path (ważne!)

    # candidates: list[CandidateRecordDto]