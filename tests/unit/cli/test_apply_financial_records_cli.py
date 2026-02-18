from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from contract_costs.cli.commands.apply import financial_records as mod
from contract_costs.services.financial_records.assigment.apply.commands.apply_invoice_excel_bach_command import (
    ApplyInvoiceExcelBatchCommand,
)


def _services(org_id, user_id):
    return SimpleNamespace(
        context=SimpleNamespace(
            current_organization_id=lambda: org_id,
            current_user_id=lambda: user_id,
        ),
        action_bus=SimpleNamespace(execute=Mock()),
        apply_financial_record_excel_batch=object(),
    )


def test_handle_apply_financial_records_with_explicit_file_does_not_mark_processed(monkeypatch) -> None:
    org_id = uuid4()
    user_id = uuid4()
    services = _services(org_id, user_id)
    monkeypatch.setattr(mod, "get_services", lambda: services)

    manager = SimpleNamespace(get_active_file=lambda: Path("active.xlsx"), mark_processed=Mock())
    monkeypatch.setattr(mod, "FinancialRecordInvoiceAssignmentFileManager", lambda organization_id: manager)

    batch = object()
    monkeypatch.setattr(mod, "load_invoice_excel_batch", lambda path: batch)

    args = SimpleNamespace(file="custom.xlsx")
    mod.handle_apply_financial_records(args)

    call = services.action_bus.execute.call_args.kwargs
    assert isinstance(call["action"], ApplyInvoiceExcelBatchCommand)
    assert call["action"].organization_id == org_id
    assert call["action"].actor_user_id == user_id
    assert call["action"].batch is batch
    assert call["handler"] is services.apply_financial_record_excel_batch
    assert manager.mark_processed.call_count == 0


def test_handle_apply_financial_records_with_managed_file_marks_processed(monkeypatch) -> None:
    org_id = uuid4()
    user_id = uuid4()
    services = _services(org_id, user_id)
    monkeypatch.setattr(mod, "get_services", lambda: services)

    active = Path("active.xlsx")
    manager = SimpleNamespace(get_active_file=lambda: active, mark_processed=Mock())
    monkeypatch.setattr(mod, "FinancialRecordInvoiceAssignmentFileManager", lambda organization_id: manager)

    monkeypatch.setattr(mod, "load_invoice_excel_batch", lambda path: object())

    args = SimpleNamespace(file=None)
    mod.handle_apply_financial_records(args)

    assert manager.mark_processed.call_count == 1


def test_handle_apply_financial_records_propagates_loader_error(monkeypatch) -> None:
    org_id = uuid4()
    user_id = uuid4()
    services = _services(org_id, user_id)
    monkeypatch.setattr(mod, "get_services", lambda: services)

    manager = SimpleNamespace(get_active_file=lambda: Path("active.xlsx"), mark_processed=Mock())
    monkeypatch.setattr(mod, "FinancialRecordInvoiceAssignmentFileManager", lambda organization_id: manager)
    monkeypatch.setattr(mod, "load_invoice_excel_batch", lambda _path: (_ for _ in ()).throw(FileNotFoundError("missing")))

    with pytest.raises(FileNotFoundError, match="missing"):
        mod.handle_apply_financial_records(SimpleNamespace(file=None))

