from dataclasses import dataclass


@dataclass(frozen=True)
class AttachedDocumentView:
    id: str
    filename: str
    document_type: str | None