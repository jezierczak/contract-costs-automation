import json
from uuid import UUID

from contract_costs.model.document import (
    Document,
    DocumentType,
    DocumentSource,
)


def map_row_to_document(row: dict) -> Document:
    return Document(
        id=UUID(row["id"]),
        organization_id=UUID(row["organization_id"]),
        financial_record_id=UUID(row["financial_record_id"]) if row["financial_record_id"] else None,
        document_source=DocumentSource(row["document_source"]),
        document_type=DocumentType(row["document_type"]) if row["document_type"] else None,
        document_number=row["document_number"],
        seller_nip=row["seller_nip"],
        parsed_payload=json.loads(row["parsed_payload"]) if row["parsed_payload"] else None,
        file_hash=row["file_hash"],
        file_path=row["file_path"],
        filename=row["filename"],
        mime_type=row.get("mime_type"),
        size=row.get("size"),
        created_at=row["created_at"],
        created_by_user_id=UUID(row["created_by_user_id"]) if row["created_by_user_id"] else None,
        updated_at=row["updated_at"],
        updated_by_user_id=UUID(row["updated_by_user_id"]) if row["updated_by_user_id"] else None,
    )
