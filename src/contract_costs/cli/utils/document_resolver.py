from uuid import UUID
from contract_costs.repository.document_repository import DocumentRepository


def resolve_document_id(
    *,
    repository: DocumentRepository,
    organization_id,
    raw_id: str,
) -> UUID:

    # jeśli pełne UUID → od razu zwróć
    try:
        return UUID(raw_id)
    except ValueError:
        pass

    # skrócony UUID
    documents = repository.list_all(
        organization_id=organization_id
    )

    matches = [
        d.id for d in documents
        if str(d.id).startswith(raw_id.lower())
    ]

    if not matches:
        raise RuntimeError(f"No document found for id prefix '{raw_id}'")

    if len(matches) > 1:
        raise RuntimeError(
            f"Ambiguous document id prefix '{raw_id}' "
            f"({len(matches)} matches)"
        )

    return matches[0]
