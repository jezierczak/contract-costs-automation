from contract_costs.model.document import Document, DocumentType


class DocumentSelector:

    @staticmethod
    def resolve_primary(documents: list[Document] | None) -> Document | None:
        if not documents:
            return None

        # 1️⃣ Invoice priority
        for doc in documents:
            if doc.document_type == DocumentType.INVOICE:
                return doc

        # 2️⃣ Fallback
        return documents[0]

    @staticmethod
    def resolve_primary_path(documents: list[Document] | None) -> str | None:
        doc = DocumentSelector.resolve_primary(documents)
        return doc.file_path if doc else None
