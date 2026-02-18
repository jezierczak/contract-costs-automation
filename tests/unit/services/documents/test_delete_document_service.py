import pytest
from uuid import uuid4

from contract_costs.services.documents.process.delete.delete_command_service import (
    DeleteDocumentService,
)
from contract_costs.services.documents.process.delete.delete_document_command import (
    DeleteDocumentCommand,
)
from tests.builders.document_builder import DocumentBuilder


def test_delete_document_raises_when_not_found(uow):
    service = DeleteDocumentService()

    with pytest.raises(RuntimeError, match="Document not found"):
        service.execute(
            action=DeleteDocumentCommand(
                organization_id=uuid4(),
                actor_user_id=uuid4(),
                document_id=uuid4(),
            ),
            uow=uow,
        )


def test_delete_document_raises_when_assigned_to_record(document_repo, uow):
    organization_id = uuid4()
    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_financial_record_id(uuid4())
        .build()
    )
    document_repo.add(document)

    service = DeleteDocumentService()

    with pytest.raises(RuntimeError, match="Cannot delete document assigned to record"):
        service.execute(
            action=DeleteDocumentCommand(
                organization_id=organization_id,
                actor_user_id=uuid4(),
                document_id=document.id,
            ),
            uow=uow,
        )


def test_delete_document_removes_unassigned_document(document_repo, uow):
    organization_id = uuid4()
    document = DocumentBuilder().with_organization_id(organization_id).build()
    document_repo.add(document)

    service = DeleteDocumentService()
    service.execute(
        action=DeleteDocumentCommand(
            organization_id=organization_id,
            actor_user_id=uuid4(),
            document_id=document.id,
        ),
        uow=uow,
    )

    assert document_repo.get(organization_id=organization_id, document_id=document.id) is None
