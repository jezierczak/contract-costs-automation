from queue import Empty
from types import SimpleNamespace
from uuid import uuid4

import pytest

from contract_costs.model.document import DocumentSource
from contract_costs.services.workers.document_parse_worker import (
    DocumentParseWorker,
)


class _OneItemQueue:
    def __init__(self, item):
        self._item = item
        self._used = False
        self.task_done_calls = 0

    def get(self, timeout=1):
        _ = timeout
        if self._used:
            raise Empty
        self._used = True
        return self._item

    def task_done(self):
        self.task_done_calls += 1

    def qsize(self):
        return 0 if self._used else 1


def test_document_parse_worker_run_processes_one_item_and_calls_task_done(monkeypatch) -> None:
    org_id, actor_id, doc_id = uuid4(), uuid4(), uuid4()
    queue = _OneItemQueue((org_id, actor_id, doc_id))

    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.document_queue",
        queue,
    )

    worker = DocumentParseWorker(rpm=60, timeout=1)

    def _fake_process(*args, **kwargs):
        _ = args, kwargs
        worker.stop()

    monkeypatch.setattr(worker, "_process_with_retry", _fake_process)

    worker.run()
    assert queue.task_done_calls == 1


def test_document_parse_worker_process_with_retry_returns_on_fatal_exit(monkeypatch) -> None:
    class _FakeProcess:
        def __init__(self, *args, **kwargs):
            self.exitcode = 100

        def start(self):
            return None

        def join(self, timeout=None):
            _ = timeout
            return None

        def is_alive(self):
            return False

    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.Process",
        _FakeProcess,
    )

    worker = DocumentParseWorker(rpm=60, timeout=1)
    worker._process_with_retry(uuid4(), uuid4(), uuid4())


def test_document_parse_worker_process_with_retry_raises_after_timeouts(monkeypatch) -> None:
    class _FakeProcess:
        def __init__(self, *args, **kwargs):
            self.exitcode = None

        def start(self):
            return None

        def join(self, timeout=None):
            _ = timeout
            return None

        def is_alive(self):
            return True

        def terminate(self):
            return None

    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.Process",
        _FakeProcess,
    )
    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.time.sleep",
        lambda *_args, **_kwargs: None,
    )

    worker = DocumentParseWorker(rpm=60, timeout=1)
    with pytest.raises(TimeoutError):
        worker._process_with_retry(uuid4(), uuid4(), uuid4())


def test_document_parse_worker_process_with_retry_retries_then_succeeds(monkeypatch) -> None:
    class _FakeProcess:
        call = 0

        def __init__(self, *args, **kwargs):
            _ = args, kwargs
            _FakeProcess.call += 1
            self._idx = _FakeProcess.call
            self.exitcode = 1 if self._idx == 1 else 0

        def start(self):
            return None

        def join(self, timeout=None):
            _ = timeout
            return None

        def is_alive(self):
            return False

    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.Process",
        _FakeProcess,
    )
    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.time.sleep",
        lambda *_args, **_kwargs: None,
    )

    worker = DocumentParseWorker(rpm=60, timeout=1)
    worker._process_with_retry(uuid4(), uuid4(), uuid4())
    assert _FakeProcess.call == 2


def test_document_parse_worker_process_with_retry_raises_after_nonzero_exit(monkeypatch) -> None:
    class _FakeProcess:
        def __init__(self, *args, **kwargs):
            _ = args, kwargs
            self.exitcode = 2

        def start(self):
            return None

        def join(self, timeout=None):
            _ = timeout
            return None

        def is_alive(self):
            return False

    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.Process",
        _FakeProcess,
    )
    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.time.sleep",
        lambda *_args, **_kwargs: None,
    )

    worker = DocumentParseWorker(rpm=60, timeout=1)
    with pytest.raises(RuntimeError, match="subprocess error"):
        worker._process_with_retry(uuid4(), uuid4(), uuid4())


def test_document_parse_worker_run_skips_sleep_for_ksef(monkeypatch) -> None:
    org_id, actor_id, doc_id = uuid4(), uuid4(), uuid4()
    queue = _OneItemQueue((org_id, actor_id, doc_id))

    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.document_queue",
        queue,
    )

    sleep_calls = {"n": 0}
    monkeypatch.setattr(
        "contract_costs.services.workers.document_parse_worker.time.sleep",
        lambda *_args, **_kwargs: sleep_calls.__setitem__("n", sleep_calls["n"] + 1),
    )

    services = SimpleNamespace(
        document_repository=SimpleNamespace(
            get=lambda **_: SimpleNamespace(document_source=DocumentSource.KSEF)
        )
    )
    monkeypatch.setattr(
        "contract_costs.cli.context.get_services",
        lambda: services,
    )

    worker = DocumentParseWorker(rpm=60, timeout=1)

    def _fake_process(*args, **kwargs):
        _ = args, kwargs
        worker.stop()

    monkeypatch.setattr(worker, "_process_with_retry", _fake_process)

    worker.run()
    assert queue.task_done_calls == 1
    assert sleep_calls["n"] == 0
