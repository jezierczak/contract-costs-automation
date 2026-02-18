import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from contract_costs.services.documents.process.dto.process_document_command import (
    ProcessDocumentCommand,
)
from contract_costs.services.documents.process.reprocess.reprocess_document_command import (
    ReprocessDocumentCommand,
)
from contract_costs.services.documents.process.reprocess.reprocess_document_service import (
    ReprocessDocumentService,
)
from tests.builders.document_builder import DocumentBuilder


def test_reprocess_raises_when_document_not_found(uow):
    service = ReprocessDocumentService(
        process_document_service=MagicMock(),
    )

    with pytest.raises(RuntimeError, match="Document not found"):
        service.execute(
            action=ReprocessDocumentCommand(
                organization_id=uuid4(),
                actor_user_id=uuid4(),
                document_id=uuid4(),
                force=False,
            ),
            uow=uow,
        )


def test_reprocess_raises_when_document_is_already_assigned(document_repo, uow):
    organization_id = uuid4()
    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_financial_record_id(uuid4())
        .build()
    )
    document_repo.add(document)

    service = ReprocessDocumentService(
        process_document_service=MagicMock(),
    )

    with pytest.raises(RuntimeError, match="already assigned"):
        service.execute(
            action=ReprocessDocumentCommand(
                organization_id=organization_id,
                actor_user_id=uuid4(),
                document_id=document.id,
                force=True,
            ),
            uow=uow,
        )


def test_reprocess_delegates_to_process_command_via_action_bus(document_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    document = DocumentBuilder().with_organization_id(organization_id).build()
    document_repo.add(document)

    process_handler = MagicMock()
    service = ReprocessDocumentService(
        process_document_service=process_handler,
    )

    service.execute(
        action=ReprocessDocumentCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            document_id=document.id,
            force=True,
        ),
        uow=uow,
    )

    process_handler.execute.assert_called_once()
    kwargs = process_handler.execute.call_args.kwargs
    assert kwargs["uow"] is uow
    assert isinstance(kwargs["action"], ProcessDocumentCommand)
    assert kwargs["action"].organization_id == organization_id
    assert kwargs["action"].actor_user_id == actor_user_id
    assert kwargs["action"].document_id == document.id
    assert kwargs["action"].force is True
