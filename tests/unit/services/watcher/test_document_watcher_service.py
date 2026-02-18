from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from contract_costs.services.documents.upload.dto.upload_document_command import (
    UploadDocumentCommand,
)
from contract_costs.services.watcher.document_watcher import DocumentWatcherService


def test_document_watcher_run_and_stop_manage_file_watcher(monkeypatch, tmp_path) -> None:
    created = {}

    class _FakeFileWatcher:
        def __init__(self, *, path, on_file_created):
            created["path"] = path
            created["cb"] = on_file_created
            self.started = False
            self.stopped = False

        def start(self):
            self.started = True

        def stop(self):
            self.stopped = True

    monkeypatch.setattr(
        "contract_costs.services.watcher.document_watcher.FileWatcher",
        _FakeFileWatcher,
    )

    services = SimpleNamespace(action_bus=Mock(), upload_document_service=Mock())
    svc = DocumentWatcherService(
        services=services,
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        watch_dir=tmp_path,
    )

    svc.run()
    assert created["path"] == tmp_path
    svc.stop()
    assert svc.watcher.stopped is True


def test_document_watcher_handle_file_executes_upload_action(monkeypatch, tmp_path) -> None:
    action_bus = Mock()
    upload_service = Mock()
    services = SimpleNamespace(action_bus=action_bus, upload_document_service=upload_service)

    org_id = uuid4()
    user_id = uuid4()
    file_path = tmp_path / "inv.pdf"
    file_path.write_text("x", encoding="utf-8")

    svc = DocumentWatcherService(
        services=services,
        organization_id=org_id,
        actor_user_id=user_id,
        watch_dir=tmp_path,
    )

    monkeypatch.setattr(
        DocumentWatcherService,
        "_wait_until_file_ready",
        staticmethod(lambda *_args, **_kwargs: True),
    )

    svc._handle_file(file_path)

    assert action_bus.execute.call_count == 1
    call = action_bus.execute.call_args.kwargs
    assert call["handler"] is upload_service
    assert isinstance(call["action"], UploadDocumentCommand)
    assert call["action"].organization_id == org_id
    assert call["action"].actor_user_id == user_id
    assert call["action"].file_path == Path(file_path)


def test_document_watcher_handle_file_skips_when_not_ready(monkeypatch, tmp_path) -> None:
    action_bus = Mock()
    services = SimpleNamespace(action_bus=action_bus, upload_document_service=Mock())
    svc = DocumentWatcherService(
        services=services,
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        watch_dir=tmp_path,
    )

    monkeypatch.setattr(
        DocumentWatcherService,
        "_wait_until_file_ready",
        staticmethod(lambda *_args, **_kwargs: False),
    )

    svc._handle_file(tmp_path / "missing.pdf")
    assert action_bus.execute.call_count == 0

